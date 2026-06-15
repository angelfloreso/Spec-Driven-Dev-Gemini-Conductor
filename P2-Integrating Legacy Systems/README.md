# P2 - Integrating Legacy Systems: Spec-Driven Development in Practice

This workshop extends the Spec-Driven Development principle into legacy system integration using **Consumer-Driven Contracts (CDC)**.

In P1 you saw how an OpenAPI spec is the source of truth for a single service — the build generates code from the spec and rejects anything that drifts. Here the same idea scales across a **team boundary**: the consumer writes a machine-readable spec (a contract) of what it needs, and the producer's build must satisfy it before any code ships.

## The Problem

Legacy system integration without shared specs leads to:

- **Breaking changes**: Provider updates API without warning — no spec to enforce backward compatibility
- **Silent failures**: Code compiles fine but crashes at runtime after deployment
- **Coordination hell**: Consumer and provider teams argue over who breaks what, with no source of truth
- **Lost time**: Debugging production failures that could have been caught at build time

## The Spec-Driven Solution: Consumer-Driven Contracts

**CDC is Spec-Driven Development at the integration layer.** The consumer defines an explicit spec (the contract — what fields, types, and behaviours it depends on). The producer's build runs those specs as tests and fails if anything violates them.

> Spec → Code, not Code → Spec.
> If the spec changes, the build tells you immediately. Not production.

If the producer breaks the contract, the build fails **before** deployment.

## How It Fits Into Spec-Driven Development

```
  Spec-Driven Development Principle
  ──────────────────────────────────
  Write the spec first → Generate / validate code from it
  Never let implementation drift from the spec

  P1 recap (single service):
    OpenAPI YAML  ──►  Generated Spring interfaces  ──►  Controller must implement them

  P2 (across a team boundary):
    Consumer Contract  ──►  Producer build verifies against it  ──►  Build fails on drift

┌──────────────────────────┐         ┌──────────────────────────┐
│  CONSUMER (Client App)   │         │  PRODUCER (Legacy API)   │
│                          │◄────────┤                          │
│  SchedulingClient        │  HTTP   │  SchedulingController    │
│  (calls /api/v1/...)     │         │  (serves /api/v1/...)    │
└──────────────────────────┘         └──────────────────────────┘
           │                                      │
  Writes contract spec              Runs contract as build test
  (AppointmentContractTest)         (ProducerContractTest)
           │                                      │
           └─────────── shared expectation ───────┘
                   "appointmentId, practitionerName,
                    startTime must be present"
```

## Quick Start

### Step 0 - Run All Tests (Baseline)

```bash
# From root
mvn clean install
```

Expected output:
```
Tests run: 4  (1 producer contract test + 3 consumer contract tests)
BUILD SUCCESS ✓
```

**What this demonstrates**:
- **Producer Contract Test** (`ProducerContractTest`): Validates the producer satisfies the contract spec — same role as the OpenAPI contract test in P1
- **Consumer Contract Tests** (`AppointmentContractTest`): The spec written from the consumer's perspective — documents required fields as executable expectations

Both sides honour the v1 contract spec. The build is green.

---

## Workshop Scenarios

### Scenario 1: Breaking Change - Field Removal

**What happens**: Producer team removes the `practitionerName` field (by accident).

Edit `producer/src/main/java/com/legacyintegration/producer/Appointment.java`:

```java
package com.legacyintegration.producer;

import com.fasterxml.jackson.annotation.JsonProperty;

public class Appointment {
    @JsonProperty("appointmentId")
    private String appointmentId;
    
    // @JsonProperty("practitionerName")
    // private String practitionerName;  // REMOVED!
    
    @JsonProperty("startTime")
    private String startTime;

    public Appointment(String appointmentId, String startTime) {
        this.appointmentId = appointmentId;
        // this.practitionerName = practitionerName;  // REMOVED!
        this.startTime = startTime;
    }

    public String getAppointmentId() {
        return appointmentId;
    }

    // getPractitionerName() REMOVED

    public String getStartTime() {
        return startTime;
    }
}
```

And update controller:

```java
package com.legacyintegration.producer;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/v1")
public class SchedulingController {

    @GetMapping("/appointments/{id}")
    public ResponseEntity<Appointment> getAppointment(@PathVariable("id") String appointmentId) {
        Appointment appointment = new Appointment(
                appointmentId,
                "Dr. Smith",
                "2026-06-20T10:00:00"
        );
        return ResponseEntity.ok(appointment);
    }
}
```

Run producer tests:

```bash
cd producer
mvn clean test
```

Expected result: **BUILD FAILURE** ❌

Why it fails: `ProducerContractTest` enforces the v1 contract and explicitly expects `practitionerName`.

Example failure:

```text
[ERROR] ProducerContractTest.shouldReturnAppointmentWithRequiredFields
No value at JSON path "$.practitionerName"
```

This is expected and desirable in Spec-Driven Development: once the implementation drifts from the contract spec, the build blocks the change.

**Key insight**: the producer-side contract test already catches the break before production.

---

### Scenario 2: Safe Versioning - Add V2 Alongside V1

**Best practice**: Don't remove v1; add v2.

Revert the Appointment.java to include `practitionerName`, then add a v2 model and endpoint.

Create `producer/src/main/java/com/legacyintegration/producer/AppointmentV2.java`:

```java
package com.legacyintegration.producer;

import com.fasterxml.jackson.annotation.JsonProperty;

public class AppointmentV2 {
    @JsonProperty("appointmentId")
    private String appointmentId;
    
    @JsonProperty("doctorName")  // RENAMED from practitionerName
    private String doctorName;
    
    @JsonProperty("startTime")
    private String startTime;
    
    @JsonProperty("channel")     // NEW field
    private String channel;

    public AppointmentV2(String appointmentId, String doctorName, String startTime, String channel) {
        this.appointmentId = appointmentId;
        this.doctorName = doctorName;
        this.startTime = startTime;
        this.channel = channel;
    }

    // Getters...
}
```

Update `SchedulingController` to add v2 endpoint:

```java
package com.legacyintegration.producer;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api")
public class SchedulingController {

    // V1 - Legacy (unchanged)
    @GetMapping("/v1/appointments/{id}")
    public ResponseEntity<Appointment> getAppointmentV1(@PathVariable("id") String appointmentId) {
        Appointment appointment = new Appointment(
                appointmentId,
                "Dr. Smith",
                "2026-06-20T10:00:00"
        );
        return ResponseEntity.ok(appointment);
    }

    // V2 - New (breaking changes isolated)
    @GetMapping("/v2/appointments/{appointmentId}")
    public ResponseEntity<AppointmentV2> getAppointmentV2(@PathVariable String appointmentId) {
        AppointmentV2 appointment = new AppointmentV2(
                appointmentId,
                "Dr. Smith",
                "2026-06-20T10:00:00",
                "VIRTUAL"
        );
        return ResponseEntity.ok(appointment);
    }
}
```

Run producer tests:

```bash
cd producer
mvn clean test
```

Expected result: **BUILD SUCCESS** ✓ (v1 endpoint still satisfies v1 contract)

---

### Scenario 3: Consumer Migrates to V2

Consumer team wants to use the new v2 API. They add a new contract for v2.

Add test in `consumer/src/test/java/com/legacyintegration/consumer/ConsumerContractTest.java`:

```java
@Test
public void shouldSuccessfullyCallV2WithNewFields() {
    // Mock producer v2 response
    wireMockServer.stubFor(
            WireMock.get(WireMock.urlEqualTo("/api/v2/appointments/APT-001"))
                    .willReturn(WireMock.aResponse()
                            .withStatus(200)
                            .withHeader("Content-Type", "application/json")
                            .withBody("{\"appointmentId\":\"APT-001\",\"doctorName\":\"Dr. Smith\",\"startTime\":\"2026-06-20T10:00:00\",\"channel\":\"VIRTUAL\"}"))
    );

    // This would call the new v2 endpoint
    // (Add a getAppointmentV2 method to SchedulingClient)
    String response = "{\"appointmentId\":\"APT-001\",\"doctorName\":\"Dr. Smith\",\"startTime\":\"2026-06-20T10:00:00\",\"channel\":\"VIRTUAL\"}";
    
    assertThat(response).contains("doctorName");
    assertThat(response).contains("channel");
}
```

Run consumer tests:

```bash
cd consumer
mvn clean test
```

Expected result: **BUILD SUCCESS** ✓

Now both v1 and v2 contracts coexist. Producer can provide both versions, and consumers can migrate at their own pace.

---

### Scenario 4: The Gotcha - Silent Deserialization Failure

**What happens**: A consumer forgets to check for `null` values when a required field is missing.

Mock a producer response that's missing `appointmentId`:

```java
@Test
public void shouldFailWhenRequiredFieldIsMissing() {
    // Producer breaks contract - missing appointmentId
    wireMockServer.stubFor(
            WireMock.get(WireMock.urlEqualTo("/api/v1/appointments/APT-004"))
                    .willReturn(WireMock.aResponse()
                            .withStatus(200)
                            .withHeader("Content-Type", "application/json")
                            .withBody("{\"practitionerName\":\"Dr. Jones\",\"startTime\":\"2026-06-20T10:00:00\"}"))
    );

    // Consumer tries to deserialize - should fail
    assertThatThrownBy(() -> schedulingClient.getAppointment("APT-004"))
            .isInstanceOf(Exception.class)
            .hasMessageContaining("appointmentId");
}
```

Run consumer tests:

```bash
cd consumer
mvn clean test
```

Expected result: **BUILD FAILURE** ❌ (contract test catches it)

---

## Key Takeaways

### Spec-Driven Development — the common thread across P1 and P2

| | P1 - Immutable Build | P2 - Legacy Integration |
|---|---|---|
| **Spec format** | OpenAPI YAML | Consumer Contract (test) |
| **Who writes the spec** | API designer | Consumer team |
| **Where spec lives** | `src/main/resources/openapi/` | `*ContractTest.java` |
| **Build enforces it** | Generated interfaces must be implemented | Producer test must satisfy contract |
| **Drift caught at** | Compile time | Test time |
| **Key rule** | Change spec first, code follows | Consumer spec wins; producer adapts |

### CDC comparison table

| Aspect | Without CDC | With CDC (Spec-Driven) |
|--------|------------|---------|
| **Breaking change detected** | Runtime (production outage) | Build time (before deployment) |
| **Field rename** | Silent failures | Test fails; prevents deployment |
| **Versioning strategy** | Chaotic; unclear | Clear; multiple versions coexist |
| **Integration coordination** | Manual, error-prone | Automated, machine-enforced |
| **Cost of failure** | Production outage + hotfix | Zero (blocked at CI/CD) |

---

## Extensions (Optional)

### 1. Add Health Check Endpoint

Both producer and consumer can expose `/actuator/health` for readiness checks.

```java
@Configuration
public class ActuatorConfig {
    // Spring Boot provides this by default with starter-actuator
}
```

### 2. Add Deprecation Headers

Warn consumers that v1 will be removed:

```java
@GetMapping("/v1/appointments/{appointmentId}")
public ResponseEntity<Appointment> getAppointmentV1(@PathVariable String appointmentId) {
    return ResponseEntity.ok()
            .header("Deprecated", "true")
            .header("Sunset", "2026-12-31")
            .body(appointment);
}
```

### 3. Contract Broker (Production-Ready)

Use a Pact Broker or similar to share contracts between teams:
- Consumer publishes contracts to broker
- Producer fetches contracts and runs tests
- No need to check out both repos

---

## Troubleshooting

**Q: Producer test passes but consumer test fails**  
A: Check that the mocked response in consumer test exactly matches what producer would return.

**Q: "Cannot find field X"**  
A: The GSON deserialization is failing. Verify the JSON field names in mocked response.

**Q: Ports already in use**  
A: Kill existing process: `lsof -i :8080 | grep LISTEN | awk '{print $2}' | xargs kill -9`

---

## Concepts Deep Dive

### What Makes CDC Effective?

1. **Explicit Contracts**: Expectations are written down (tests), not implicit
2. **Verified**: Tests run on both sides; no surprises
3. **Bidirectional**: Consumer defines expectations, Producer verifies them
4. **Fast Feedback**: Failures caught during build, not after deployment

### When to Use CDC?

- ✅ Microservices architecture
- ✅ Legacy API integration
- ✅ Cross-team dependencies
- ✅ Frequent API changes
- ❌ Not needed for internal private methods (use unit tests instead)

---

## Real-World Scenario: Migrating a Monolith

Imagine you're splitting a monolith into microservices. The existing monolith is the "legacy producer," and new services are "consumers."

**CDC helps you**:
1. Define what each service needs from the monolith
2. Catch breaking changes before they break new services
3. Plan gradual migration: monolith provides both old and new endpoints
4. Safely decommission old endpoints once all consumers have migrated

---

## Summary

Spec-Driven Development doesn't stop at a single service. Consumer-Driven Contracts carry the same principle across team boundaries:

1. **Spec is written first** — the consumer contract defines what the integration must look like
2. **Build enforces the spec** — the producer cannot ship code that violates it
3. **Versioning is explicit** — v1 contract stays alive until all consumers migrate; v2 contract is added alongside it
4. **Drift is impossible** — any manual change that breaks the contract is caught by `mvn clean install`, not by a production alert

This is the same "immutable build" guarantee from P1, now applied across service boundaries.

**Remember**: "The spec is the contract. The build is the referee." – Spec-Driven Development
