# P4 Tutorial - Generate Spring API From OpenAPI YAML

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
cd "/root/projects/SpecDrivenDev-Conductor/P4-OpenAPI Generator"
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

## Step 5 - Exercise: Add New Endpoint And Implement Generated Interface

Update api-spec.yaml to add a new endpoint and response schema:

``` yaml

openapi: 3.0.3
info:
  title: MedSched API
  description: API for managing medical appointments, patient onboarding, and schedule control.
  version: 1.0.0
  contact:
    name: Technical Lead Practice
    email: support@medsched.example.com
servers:
  - url: https://api.medsched.example.com/v1
    description: Production server

paths:
  /patients:
    post:
      summary: Register new patient (FR-01.1)
      operationId: registerPatient
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/PatientRegistration'
      responses:
        '201':
          description: Patient registered successfully
        '409':
          description: Patient already exists (FR-01.2 - De-duplication)

  /appointments:
    post:
      summary: Book appointment (FR-02.1)
      description: Books a slot and temporarily locks it for 5 minutes to prevent concurrency.
      operationId: bookAppointment
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/AppointmentRequest'
      responses:
        '201':
          description: Appointment booked
        '423':
          description: Slot locked or unavailable

  /appointments/{appointmentId}/cancel:
    post:
      summary: Cancel appointment (FR-02.3)
      operationId: cancelAppointment
      parameters:
        - name: appointmentId
          in: path
          required: true
          schema:
            type: string
      responses:
        '200':
          description: Appointment cancelled, slot released

  /appointments/{appointmentId}:
    get:
      summary: Get appointment details (FR-02.5)
      operationId: getAppointmentById
      parameters:
        - name: appointmentId
          in: path
          required: true
          schema:
            type: string
      responses:
        '200':
          description: Appointment details found
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/AppointmentDetails'
        '404':
          description: Appointment not found

  /practitioners/{practitionerId}/schedule-blocks:
    post:
      summary: Block schedule (FR-02.4)
      operationId: blockSchedule
      parameters:
        - name: practitionerId
          in: path
          required: true
          schema:
            type: string
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/ScheduleBlock'
      responses:
        '201':
          description: Block registered

components:
  schemas:
    PatientRegistration:
      type: object
      required:
        - fullName
        - dob
        - phone
        - email
      properties:
        fullName:
          type: string
          description: Full legal name
        dob:
          type: string
          format: date
        sex:
          type: string
          enum: [M, F, Other]
        phone:
          type: string
        email:
          type: string
          format: email
        govtIdToken:
          type: string
          description: Government ID token for de-duplication (FR-01.2)
        allergies:
          type: array
          items:
            type: string

    AppointmentRequest:
      type: object
      required:
        - practitionerId
        - specialty
        - startTime
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

    ScheduleBlock:
      type: object
      required:
        - startTime
        - endTime
      properties:
        startTime:
          type: string
          format: date-time
        endTime:
          type: string
          format: date-time
        reason:
          type: string
          description: Example 'Symposium' or 'Absence'

    AppointmentDetails:
      type: object
      required:
        - appointmentId
        - practitionerId
        - specialty
        - startTime
        - status
      properties:
        appointmentId:
          type: string
        practitionerId:
          type: string
        specialty:
          type: string
        startTime:
          type: string
          format: date-time
        patientId:
          type: string
        status:
          type: string
          enum: [BOOKED, CANCELLED, COMPLETED]
```

Run the full flow:

```bash
mvn clean install
```

BUILD FAILURE is expected because the generated interface has a new method signature that is not yet implemented in the controller.

Lets implement the new endpoint in the controller:

```java
package com.p4.openapi.controller;

import com.specdrivendev.p4.api.DefaultApi;
import com.specdrivendev.p4.model.AppointmentDetails;
import com.specdrivendev.p4.model.AppointmentRequest;
import com.specdrivendev.p4.model.PatientRegistration;
import com.specdrivendev.p4.model.ScheduleBlock;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class MedSchedApiController implements DefaultApi {

    @Override
    public ResponseEntity<Void> blockSchedule(String practitionerId, ScheduleBlock scheduleBlock) {
        return ResponseEntity.status(HttpStatus.CREATED).build();
    }

    @Override
    public ResponseEntity<Void> bookAppointment(AppointmentRequest appointmentRequest) {
        return ResponseEntity.status(HttpStatus.CREATED).build();
    }

    @Override
    public ResponseEntity<Void> cancelAppointment(String appointmentId) {
        return ResponseEntity.ok().build();
    }

    @Override
    public ResponseEntity<AppointmentDetails> getAppointmentById(String appointmentId) {
        AppointmentDetails details = new AppointmentDetails();
        details.setAppointmentId(appointmentId);
        details.setPractitionerId("PRAC-001");
        details.setSpecialty("General Medicine");
        details.setStartTime(java.time.OffsetDateTime.parse("2026-07-01T10:00:00Z"));
        details.setPatientId("PAT-1001");
        details.setStatus(AppointmentDetails.StatusEnum.BOOKED);
        return ResponseEntity.ok(details);
    }

    @Override
    public ResponseEntity<Void> registerPatient(PatientRegistration patientRegistration) {
        return ResponseEntity.status(HttpStatus.CREATED).build();
    }
}
```

Run the full flow:

```bash
cd "/root/projects/SpecDrivenDev-Conductor/P4-OpenAPI Generator"
mvn clean install
```

Now the build should succeed because the controller implements all methods from the generated DefaultApi interface.

1. api-spec.yaml includes a endpoints:
2. api-spec.yaml includes a new response schemas:
3. src/main/java/com/p4/openapi/controller/MedSchedApiController.java implements the generated DefaultApi interface.

Then run the app:

```bash
mvn spring-boot:run
```

Test the new endpoints:

```bash
curl http://localhost:8080/appointments/APT-001
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
