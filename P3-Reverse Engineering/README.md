# P6 Tutorial - Reverse Engineering: Generate OpenAPI Spec From Code

This practice teaches **reverse-engineering** — extracting a machine-readable OpenAPI specification from existing Spring Boot code using `springdoc-openapi`.

> **Context in the course**
> P1–P5 work **spec-first** (write YAML, generate code).
> P6 works **code-first** (annotate existing code, generate YAML).
> Both directions are real-world skills. Use reverse engineering when you inherit a legacy codebase with no spec.

---

## What You Will Learn

1. How `springdoc-openapi` auto-generates `/v3/api-docs` from Spring Boot controllers.
2. How `@Tag`, `@Operation`, `@ApiResponse`, `@Parameter`, and `@Schema` improve generated spec quality.
3. How to export the generated YAML and turn it into a versioned contract.
4. The difference between a **bare** spec (no annotations) and a **rich** spec (fully annotated).
5. Why adding annotations to legacy code is the first step before migrating to spec-first development.

---

## Project Structure

```
P6-Reverse Engineering/
├── pom.xml
├── src/main/
│   ├── resources/
│   │   └── application.properties        ← springdoc configuration
│   └── java/com/specdrivendev/p6/
│       ├── P6ReverseEngineeringApplication.java
│       ├── config/
│       │   └── OpenApiConfig.java        ← API title, version, server info
│       ├── model/
│       │   ├── PatientRegistration.java  ← fully annotated @Schema model
│       │   ├── AppointmentRequest.java   ← fully annotated @Schema model
│       │   └── AppointmentDetails.java   ← fully annotated @Schema model
│       └── controller/
│           ├── PatientController.java    ← fully annotated (reference)
│           ├── AppointmentController.java← fully annotated (reference)
│           └── PractitionerController.java ← BARE (your exercise target)
```

---

## Prerequisites

- Java 17+
- Maven 3.9+
- A browser

---

## Step 1 - Build and Start the Application

```bash
cd "/root/projects/SpecDrivenDev-Conductor/P6-Reverse Engineering"
mvn clean install
mvn spring-boot:run
```

Expected result: application starts on port 8080.

---

## Step 2 - Open Swagger UI

Navigate to:

```
http://localhost:8080/swagger-ui.html
```

You will see a live API explorer auto-generated from the Spring Boot controllers.

Explore the UI:
- expand the **patients** tag and the **appointments** tag
- look at the `POST /appointments` form — it shows request body schema, field descriptions, and example values
- look at the **default** group — this is `PractitionerController`, which has **no annotations yet**

---

## Step 3 - Fetch the Raw OpenAPI JSON Spec

springdoc-openapi serves the spec at:

```bash
curl http://localhost:8080/v3/api-docs | python3 -m json.tool
```

To get it as YAML instead, add the suffix:

```bash
curl http://localhost:8080/v3/api-docs.yaml
```

---

## Step 4 - Export and Save the Generated Spec

Save the spec to a file:

```bash
curl http://localhost:8080/v3/api-docs.yaml -o generated-spec.yaml
```

Open `generated-spec.yaml` and notice:
- `PatientController` and `AppointmentController` have rich summaries, descriptions, and documented response codes.
- `PractitionerController` endpoints appear as generic `GET /practitioners/{practitionerId}/queue` with no descriptions, no response codes, and no parameter docs.

This is the **before/after** contrast the next step addresses.

---

## Step 5 - Understand the Annotation Toolkit

These are the springdoc / Swagger v3 annotations used in this project:

### On controllers / methods

| Annotation | Purpose | Example |
|---|---|---|
| `@Tag(name, description)` | Groups endpoints in Swagger UI | `@Tag(name = "patients", description = "Patient management")` |
| `@Operation(summary, description)` | Documents a single endpoint | `@Operation(summary = "Register patient (FR-01.1)")` |
| `@ApiResponse(responseCode, description)` | Documents one HTTP response | `@ApiResponse(responseCode = "409", description = "Already exists")` |
| `@ApiResponses({...})` | Wraps multiple responses | wraps a list of `@ApiResponse` |
| `@Parameter(description, example)` | Documents a path/query param | `@Parameter(description = "Appointment ID")` |

### On model fields

| Annotation | Purpose |
|---|---|
| `@Schema(description, example)` | Human-readable field documentation |
| `@Schema(requiredMode = REQUIRED)` | Marks field as required in the spec |
| `@Schema(allowableValues = {...})` | Documents enum-like constraints |

### In `OpenApiConfig`

| Bean method | Purpose |
|---|---|
| `OpenAPI.info(...)` | Sets title, version, contact |
| `OpenAPI.servers(...)` | Defines server URLs shown in Swagger UI |

---

## Step 6 - Exercise: Annotate PractitionerController

Open `PractitionerController.java`:

```
src/main/java/com/specdrivendev/p6/controller/PractitionerController.java
```

It currently has **no springdoc annotations**. Add the following:

### 6.1 Add `@Tag` to the class

```java
@Tag(name = "practitioners", description = "Practitioner queue and schedule blocks (FR-02.4, FR-04.2)")
```

### 6.2 Annotate `getQueue`

```java
@Operation(
    summary = "Get practitioner's waiting room queue (FR-04.2)",
    description = "Returns today's ordered appointment list for the given practitioner."
)
@ApiResponses({
    @ApiResponse(responseCode = "200", description = "Queue returned",
        content = @Content(array = @ArraySchema(schema = @Schema(implementation = AppointmentDetails.class)))),
    @ApiResponse(responseCode = "404", description = "Practitioner not found", content = @Content)
})
```

Add `@Parameter` to the path variable:

```java
@Parameter(description = "Unique practitioner ID", example = "PRAC-001")
@PathVariable String practitionerId
```

### 6.3 Annotate `blockSchedule`

```java
@Operation(
    summary = "Block practitioner schedule (FR-02.4)",
    description = "Registers a calendar block such as a symposium or absence."
)
@ApiResponses({
    @ApiResponse(responseCode = "201", description = "Block registered"),
    @ApiResponse(responseCode = "404", description = "Practitioner not found", content = @Content)
})
```

### 6.4 Rebuild and refresh Swagger UI

```bash
mvn spring-boot:run
```

Refresh `http://localhost:8080/swagger-ui.html`.

Expected result:
- **practitioners** tag now appears as a named group.
- Both endpoints show summaries, descriptions, and response codes.
- `getQueue` shows the `AppointmentDetails` response schema.

---

## Step 7 - Compare Before and After

Export the spec again after your changes:

```bash
curl http://localhost:8080/v3/api-docs.yaml -o generated-spec-annotated.yaml
diff generated-spec.yaml generated-spec-annotated.yaml
```

The diff shows exactly how much information the annotations added to the contract.

Key things to look for in `generated-spec-annotated.yaml`:

- [ ] `/practitioners/{practitionerId}/queue` now has a `tags:` entry with `practitioners`.
- [ ] `summary:` and `description:` are populated for both endpoints.
- [ ] `responses:` section includes `200`, `201`, and `404` with descriptions.
- [ ] Path parameter `practitionerId` has a `description` and `example`.
- [ ] The response body schema references `AppointmentDetails`.

---

## Step 8 - Export Spec and Validate

Once satisfied, export the final spec and validate it:

```bash
curl http://localhost:8080/v3/api-docs.yaml -o medsched-reverse-engineered.yaml
```

Validate at https://editor.swagger.io — paste the YAML content. Errors appear in the right panel.

---

## Step 9 - Compare Against P5 Reference Spec

The P5 folder contains a hand-crafted spec built from the same requirements:

```bash
diff medsched-reverse-engineered.yaml \
     "../P5-NL Specs/medsched-reference.yaml"
```

This comparison answers: **how closely does reverse engineering match spec-first design?**

Common gaps you will find:
- FR coverage: reverse engineering only documents what is implemented; spec-first documents everything required.
- Response codes: unannotated code often produces only `200`; spec-first captures `201`, `409`, `423`.
- Descriptions: code reveals structure, not intent; annotations bridge the gap.

---

## Key Takeaways

| | Code-first (Reverse Engineering) | Spec-first (P1, P4) |
|---|---|---|
| **Starting point** | Existing code | OpenAPI YAML |
| **Output** | Generated spec | Generated code |
| **Annotation effort** | High (must annotate everything) | None (spec is complete) |
| **Spec quality** | Only as good as annotations | Fully controlled |
| **When to use** | Legacy systems, brownfield projects | New projects, greenfield |

**Rule of thumb**: use reverse engineering to bootstrap a spec from legacy code, then migrate to spec-first for all future changes.

---

## Quick Reference: Common springdoc Properties

```properties
# application.properties

# JSON spec endpoint
springdoc.api-docs.path=/v3/api-docs

# Swagger UI endpoint
springdoc.swagger-ui.path=/swagger-ui.html

# Sort endpoints alphabetically in Swagger UI
springdoc.swagger-ui.operations-sorter=alpha

# Show full request/response details by default
springdoc.swagger-ui.default-models-expand-depth=1

# Disable the spec endpoint (for production deployments)
# springdoc.api-docs.enabled=false

# Disable Swagger UI (for production deployments)
# springdoc.swagger-ui.enabled=false
```
