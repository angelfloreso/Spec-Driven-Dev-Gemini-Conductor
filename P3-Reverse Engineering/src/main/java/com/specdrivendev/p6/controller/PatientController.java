package com.specdrivendev.p6.controller;

import com.specdrivendev.p6.model.PatientRegistration;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.media.Content;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

@RestController
@RequestMapping("/patients")
@Tag(name = "patients", description = "Patient onboarding and management (FR-01)")
public class PatientController {

    @Operation(
        summary = "Register a new patient (FR-01.1)",
        description = "Creates a new patient record. Returns 409 if a patient with the same govtIdToken already exists (FR-01.2 de-duplication)."
    )
    @ApiResponses({
        @ApiResponse(responseCode = "201", description = "Patient registered successfully"),
        @ApiResponse(responseCode = "400", description = "Validation error – required fields missing", content = @Content),
        @ApiResponse(responseCode = "409", description = "Patient already exists (de-duplication conflict)", content = @Content)
    })
    @PostMapping
    public ResponseEntity<Map<String, String>> registerPatient(@Valid @RequestBody PatientRegistration body) {
        // In a real implementation, persist the patient here
        String patientId = "PAT-" + System.currentTimeMillis();
        return ResponseEntity.status(HttpStatus.CREATED).body(Map.of("patientId", patientId));
    }
}
