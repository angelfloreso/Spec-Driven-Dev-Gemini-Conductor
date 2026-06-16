package com.legacyintegration.producer;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.web.servlet.MockMvc;

import static org.hamcrest.Matchers.*;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@SpringBootTest
@AutoConfigureMockMvc
public class ProducerContractTest {

    @Autowired
    private MockMvc mockMvc;

    @Test
    public void shouldReturnAppointmentWithRequiredFields() throws Exception {
        // Consumer contract: /api/v1/appointments/{id} must return appointmentId, practitionerName, startTime
        mockMvc.perform(get("/api/v1/appointments/APT-001"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.appointmentId").value("APT-001"))
                .andExpect(jsonPath("$.practitionerName").exists())
                .andExpect(jsonPath("$.startTime").exists())
                .andExpect(jsonPath("$.appointmentId", notNullValue()))
                .andExpect(jsonPath("$.practitionerName", notNullValue()))
                .andExpect(jsonPath("$.startTime", notNullValue()));
    }
}
