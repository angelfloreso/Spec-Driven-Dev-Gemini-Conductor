# P2 - Integrating Legacy Systems with Consumer-Driven Contracts

A hands-on workshop demonstrating **Consumer-Driven Contracts (CDC)** for safely managing breaking changes when integrating with legacy APIs.

## The Problem

When integrating with a legacy API provider, you face risks:

- **Breaking changes**: Provider updates API without warning
- **Silent failures**: Code compiles, but fails at runtime after deployment  
- **Coordination hell**: Consumer and provider teams disagree on what to change first
- **Lost time**: Debugging production failures that could have been caught earlier

## The Solution: Consumer-Driven Contracts

**CDC shifts the paradigm**: Instead of the consumer adapting to whatever the producer provides, the consumer defines a **contract** (expectations) that the producer **must** satisfy.

If the producer breaks the contract, the build fails **before** deployment.

## Architecture

```
┌─────────────────┐         ┌──────────────────┐
│   CONSUMER      │         │    PRODUCER      │
│   (Client App)  │◄────────┤ (Legacy API)     │
└─────────────────┘         └──────────────────┘
        │                           │
        │                           │
     Defines              Validates Against
     Contract             Contract
        │                           │
        ▼                           ▼
  SchedulingClient         ProducerContractTest
  (expects v1 API)        (verifies v1 response)
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
- **Producer Contract Test** (`ProducerContractTest`): Validates that the producer API satisfies the consumer's contract expectations
- **Consumer Contract Tests** (`AppointmentContractTest`): Documents what fields the consumer expects from the producer

Both producer and consumer satisfy the v1 contract.

---

## Workshop Scenarios

### Scenario 1: Breaking Change - Field Removal

**What happens**: Producer team removes the `practitionerName` field (by accident).

Edit `producer/src/main/java/com/legacyintegration/producer/Appointment.java`:

```java
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
@GetMapping("/appointments/{id}")
public ResponseEntity<Appointment> getAppointment(@PathVariable("id") String appointmentId) {
    Appointment appointment = new Appointment(
            appointmentId,
            // removed practitionerName from constructor
            "2026-06-20T10:00:00"
    );
    return ResponseEntity.ok(appointment);
}
```

Run producer tests:

```bash
cd producer
mvn clean test
```

Expected result: **BUILD SUCCESS** ✓ (producer test only validates what it returns)

The producer test passes because it just verifies the response has those three fields. But now run a manual test:

```bash
# Start producer
mvn spring-boot:run &

# Try calling the API in another terminal
curl http://localhost:8080/api/v1/appointments/APT-001
# Response now missing "practitionerName"!
```

**The problem**: Code runs fine, but consumer will fail at deserialization because it expects `practitionerName`.

**How CDC catches this**: Consumer contract tests document the requirement. If you add a real integration test in the consumer that calls the producer API, it will fail:

```java
@Test
public void consumerFailsWhenPractitionerNameIsRemoved() {
    // This would fail because practitionerName is now missing
    SchedulingClient.AppointmentDTO appointment = client.getAppointment("APT-001");
    assertThat(appointment.practitionerName).isNotNull(); // FAILS!
}
```

**Key insight**: CDC fails the build *before* production when the contract is violated.

---

### Scenario 2: Safe Versioning - Add V2 Alongside V1

**Best practice**: Don't remove v1; add v2.

Revert the Appointment.java to include `practitionerName`, then add a v2 model and endpoint.

Create `producer/src/main/java/com/legacyintegration/producer/AppointmentV2.java`:

```java
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
@RestController
@RequestMapping("/api")
public class SchedulingController {

    // V1 - Legacy (unchanged)
    @GetMapping("/v1/appointments/{appointmentId}")
    public ResponseEntity<Appointment> getAppointmentV1(@PathVariable String appointmentId) {
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

| Aspect | Without CDC | With CDC |
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

Consumer-Driven Contracts are a defensive strategy against integration failures. By letting the consumer define what it needs and having the producer verify it can provide that, you catch breaking changes at build time instead of runtime.

This is especially valuable for legacy system integration where change coordination is difficult and the cost of downtime is high.

**Remember**: "Fail fast, fail early, fail before production." – CDC Philosophy
