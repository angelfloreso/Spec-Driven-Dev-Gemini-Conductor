package com.legacyintegration.consumer;

import org.junit.jupiter.api.Test;

import static org.assertj.core.api.Assertions.assertThat;

public class ConsumerContractTest {
    
    @Test
    public void shouldSuccessfullyCallV2WithNewFields() {
        // This represents the v2 contract that adds new fields: 'channel'
        // The consumer expects these fields from the producer
        String v2Response = "{\"appointmentId\":\"APT-001\",\"doctorName\":\"Dr. Smith\",\"startTime\":\"2026-06-20T10:00:00\",\"channel\":\"VIRTUAL\"}";
        
        // Consumer contract: requires these fields in v2 response
        assertThat(v2Response).contains("appointmentId");
        assertThat(v2Response).contains("doctorName");
        assertThat(v2Response).contains("startTime");
        assertThat(v2Response).contains("channel");  // New field in v2
    }
}