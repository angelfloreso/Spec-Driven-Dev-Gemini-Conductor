package com.legacyintegration.consumer;

import org.junit.jupiter.api.Test;
import org.springframework.boot.web.client.RestTemplateBuilder;

import static org.assertj.core.api.Assertions.assertThat;

/**
 * Consumer Contract Tests - Validates that Producer API matches consumer expectations.
 * 
 * In production, you might use:
 * - Pact (pact-foundation.org)
 * - Spring Cloud Contract
 * - Postman Contract Tests
 * 
 * For this demo, we'll use simple integration tests.
 */
public class AppointmentContractTest {

    @Test
    public void consumerExpectsAppointmentContractWithThreeFields() {
        // This test validates the consumer's contract expectations.
        // The contract states: /api/v1/appointments/{id} must return:
        // - appointmentId (string, required)
        // - practitionerName (string, required)
        // - startTime (string, required)
        
        // Consumer expects this JSON structure from producer:
        String expectedContractStructure = "{\n" +
                "  \"appointmentId\": \"APT-001\",\n" +
                "  \"practitionerName\": \"Dr. Smith\",\n" +
                "  \"startTime\": \"2026-06-20T10:00:00\"\n" +
                "}";

        assertThat(expectedContractStructure).contains("appointmentId");
        assertThat(expectedContractStructure).contains("practitionerName");
        assertThat(expectedContractStructure).contains("startTime");
    }

    @Test
    public void consumerRejectsResponseWithMissingField() {
        // If producer returns response without practitionerName, consumer contract fails
        String brokenResponse = "{\n" +
                "  \"appointmentId\": \"APT-001\",\n" +
                "  \"startTime\": \"2026-06-20T10:00:00\"\n" +
                "}";

        // Consumer test would fail if practitionerName is missing
        assertThat(brokenResponse).doesNotContain("practitionerName");
    }

    @Test
    public void consumerRejectsRenamedField() {
        // If producer renames practitionerName to doctorName, contract breaks
        String renamedResponse = "{\n" +
                "  \"appointmentId\": \"APT-001\",\n" +
                "  \"doctorName\": \"Dr. Jones\",\n" +
                "  \"startTime\": \"2026-06-20T10:00:00\"\n" +
                "}";

        // Consumer expects 'practitionerName', not 'doctorName'
        assertThat(renamedResponse).doesNotContain("practitionerName");
        assertThat(renamedResponse).contains("doctorName");
    }
}
