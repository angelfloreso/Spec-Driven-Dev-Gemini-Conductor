# Tutorial - Generate Spring API From OpenAPI YAML

This practice shows how to use openapi-generator-maven-plugin to generate Spring API interfaces and models from api-spec.yaml.

## What You Will Learn

1. how to configure openapi-generator-maven-plugin in Maven,
2. how Maven generates API contracts from YAML during build,
3. how spec-first development catches contract drift early.

## Project Files

- api-spec.yaml: source-of-truth API contract.
- pom.xml: Maven build with OpenAPI Generator plugin.
- src/main/java/com/p4/openapi/P4OpenApiGeneratorApplication.java: Spring Boot entry point.

## Prerequisites

- Java 17+
- Maven 3.9+

## Step 1 - Generate API Code From Spec

From this folder:

```bash
cd "/root/projects/SpecDrivenDev-Conductor/P2-OpenAPI Generator"
mvn clean generate-sources
```

Expected result:
- generated interfaces and models are created under target/generated-sources/openapi.

## Step 2 - Build The Project

```bash
mvn clean install
```

Expected result:
- build succeeds,
- generated code is compiled as part of the Maven lifecycle.

## Step 3 - Inspect Generated API Artifacts

Check generated files:

```bash
find target/generated-sources/openapi -type f | head -n 30
```

Look for:
- API interfaces in com.specdrivendev.p4.api
- model classes in com.specdrivendev.p4.model

## Step 4 - Practice Spec-Driven Change

Edit api-spec.yaml and add a new field to AppointmentRequest, for example:

```yaml
    AppointmentRequest:
      type: object
      required:
        - practitionerId
        - specialty
        - startTime
        - channel
      properties:
        practitionerId:
          type: string
        specialty:
          type: string
        startTime:
          type: string
          format: date-time
        patientId:
          type: string
        channel:
          type: string
          enum: [IN_PERSON, VIRTUAL]
```

Regenerate and rebuild:

```bash
mvn clean install
```

What this demonstrates:
- YAML changes become Java contract changes automatically.
- implementation must follow generated contract.

## Step 5 - Exercise 2: Add New Endpoint And Implement Generated Interface

In this repository, the second practice is already prepared for you:

1. api-spec.yaml includes a new endpoint:
  - GET /appointments/{appointmentId}
2. api-spec.yaml includes a new response schema:
  - AppointmentDetails
3. src/main/java/com/p4/openapi/controller/MedSchedApiController.java implements the generated DefaultApi interface.

Run the full flow:

```bash
cd "/root/projects/SpecDrivenDev-Conductor/P2-OpenAPI Generator"
mvn clean install
```

Then run the app:

```bash
mvn spring-boot:run
```

Test the new endpoint:

```bash
curl http://localhost:8090/appointments/APT-001
```

Expected result:
- HTTP 200
- JSON payload with fields from AppointmentDetails, such as appointmentId, practitionerId, specialty, startTime, patientId, and status.

What this demonstrates:
- OpenAPI spec defines the contract first.
- Maven generator updates Java interface/model artifacts.
- Controller implementation must match generated method signatures and response model.

## Common Commands

```bash
# Generate only
mvn generate-sources

# Full verification build
mvn clean install

# Skip tests if you only want code generation + compile
mvn clean package -DskipTests
```

## Teaching Script (Quick)

1. YAML is the source of truth.
2. Maven generates API contract classes from YAML.
3. Contract changes are visible immediately in generated Java code.
4. Teams implement against generated artifacts to avoid drift.
