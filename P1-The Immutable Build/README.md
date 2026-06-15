# The Immutable Build - Spec-Driven Development Demo (Maven + Spring Boot)

This workshop demonstrates **spec-driven development** with a deliberate break/fix cycle.

## What You Will Demo

- Start from an **outdated OpenAPI spec** and a matching implementation.
- Update the spec to a new contract.
- Run `mvn clean install` and observe compile/test failures (expected).
- Update implementation to satisfy the new contract.
- Re-run `mvn clean install` and verify green build.
- Introduce a manual contract violation in controller/service and watch contract tests reject it.

## Project Layout

- `src/main/resources/openapi/api-spec.yaml`: source-of-truth API contract.
- `openapi-generator-maven-plugin` in `pom.xml`: generates Spring API interfaces/models during build.
- `AppointmentsController` implements generated interface.
- `ApiContractTest` validates endpoint request/response against the same OpenAPI document.

## Prerequisites

- Java 17+
- Maven 3.9+

## Step 0 - Baseline Build (Should Pass)

From this folder:

```bash
mvn clean install
```

Why it passes:
- Controller/service currently match the **v1 (outdated) spec**.
- Contract test validates response against v1 schema.

## Step 1 - Update the Spec (The Intentional Break)

Edit `src/main/resources/openapi/api-spec.yaml` and replace the current endpoint definition with the following updated contract:

```yaml
openapi: 3.0.3
info:
  title: Immutable Build Scheduling API
  version: 2.0.0
  description: Updated target contract for the workshop
servers:
  - url: http://localhost:8080
tags:
  - name: appointments
paths:
  /api/appointments/next:
    get:
      tags:
        - appointments
      operationId: getNextAppointment
      summary: Get the next appointment slot for a member
      parameters:
        - in: query
          name: memberId
          required: true
          schema:
            type: string
      responses:
        '200':
          description: Next appointment slot
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/NextAppointmentResponse'
components:
  schemas:
    NextAppointmentResponse:
      type: object
      required:
        - memberId
        - practitioner
        - slotStart
        - slotEnd
        - channel
      properties:
        memberId:
          type: string
        practitioner:
          type: string
        slotStart:
          type: string
          format: string
        slotEnd:
          type: string
          format: string
        channel:
          type: string
```

## Step 2 - Run Build (Expected Failure)

```bash
mvn clean install
```

Expected result:
- Build fails because generated interfaces/models changed.
- Existing controller/service signatures and field mappings no longer compile.
- Contract test may also fail until query parameter and payload shape are updated.

## Step 3 - Implement to Match Spec v2

Update AppointmentsController.java, SchedulingService.java, and ApiContractTest.java to match the new contract.

AppointmentsController.java
```java
package com.immutablebuild.demo.controller;

import com.immutablebuild.demo.api.AppointmentsApi;
import com.immutablebuild.demo.api.model.NextAppointmentResponse;
import com.immutablebuild.demo.service.SchedulingService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class AppointmentsController implements AppointmentsApi {

    private final SchedulingService schedulingService;

    public AppointmentsController(SchedulingService schedulingService) {
        this.schedulingService = schedulingService;
    }

    @Override
    public ResponseEntity<NextAppointmentResponse> getNextAppointment(String memberId) {
        NextAppointmentResponse response = schedulingService.findNextAppointment(memberId);
        return ResponseEntity.ok(response);
    }
}
```

SchedulingService.java

```java
package com.immutablebuild.demo.service;

import com.immutablebuild.demo.api.model.NextAppointmentResponse;
import java.time.LocalDate;
import org.springframework.stereotype.Service;

@Service
public class SchedulingService {

    public NextAppointmentResponse findNextAppointment(String memberId) {
        NextAppointmentResponse response = new NextAppointmentResponse();
        response.memberId(memberId);
        response.practitioner("Dr. Alice Gray");
        response.slotStart("2024-06-15T10:00:00");
        response.slotEnd("2024-06-15T11:00:00");
        response.channel("In-person");
        return response;
    }
}
```
Why ApiContractTest may need edits:

When the contract changes first, anything validated against that contract must be updated

- The v2 spec makes memberId a required query parameter.
- Contract validation uses the same OpenAPI file, so tests must send inputs and expect payload shapes that match the updated spec.

ApiContractTest.java
```java
@Test
void endpointResponseMatchesCurrentOpenApiSpec() {
    RestAssured.baseURI = "http://localhost";
    RestAssured.port = port;

    OpenApiValidationFilter contract =
      new OpenApiValidationFilter("src/main/resources/openapi/api-spec.yaml");

    given()
      .filter(contract)
      .queryParam("memberId", "101")
    .when()
      .get("/api/appointments/next")
    .then()
      .statusCode(200);
}
```

Then run:

```bash
mvn clean install
```

Expected result:
- Build passes.
- Contract test is green.

## Step 4 - The Gotcha (Manual Contract Violation)

Now intentionally break contract without changing the YAML spec.

Example:
- In controller/service, set `slotEnd` to `null` (or omit/incorrectly map required fields).

Run:

```bash
mvn clean test
```

Expected result:
- `ApiContractTest` fails because response no longer satisfies required OpenAPI schema.
- This demonstrates that the pipeline enforces contract alignment and rejects ad-hoc drift.

## Teaching Script (Quick)

1. "Spec is source of truth."
2. "Code is generated/validated from spec."
3. "Spec change first -> code breaks fast."
4. "Implement to satisfy contract -> build green."
5. "Manual drift -> contract tests fail."

---