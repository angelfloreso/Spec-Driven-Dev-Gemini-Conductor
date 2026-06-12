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
          format: date-time
        slotEnd:
          type: string
          format: date-time
        channel:
          type: string
          enum: [VIRTUAL, IN_PERSON]
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

Update:
- `AppointmentsController#getNextAppointment(...)` to use `memberId` (`String`) query parameter.
- Service mapping to return the v2 fields:
  - `memberId`
  - `practitioner`
  - `slotStart`
  - `slotEnd`
  - `channel`

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

If you want, you can extend this by adding a CI pipeline (GitHub Actions) that runs `mvn clean verify` on pull requests.
