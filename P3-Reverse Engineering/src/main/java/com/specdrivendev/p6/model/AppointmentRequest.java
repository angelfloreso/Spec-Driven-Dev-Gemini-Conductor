package com.specdrivendev.p6.model;

import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;

import java.time.OffsetDateTime;

@Schema(description = "Appointment booking request")
public class AppointmentRequest {

    @Schema(description = "ID of the practitioner", example = "PRAC-001", requiredMode = Schema.RequiredMode.REQUIRED)
    @NotBlank
    private String practitionerId;

    @Schema(description = "Medical specialty", example = "General Medicine", requiredMode = Schema.RequiredMode.REQUIRED)
    @NotBlank
    private String specialty;

    @Schema(description = "Desired appointment start time (ISO 8601)", example = "2026-07-01T10:00:00Z", requiredMode = Schema.RequiredMode.REQUIRED)
    @NotNull
    private OffsetDateTime startTime;

    @Schema(description = "ID of the patient booking the appointment", example = "PAT-1001")
    private String patientId;

    @Schema(description = "Appointment channel", allowableValues = {"IN_PERSON", "VIRTUAL"}, example = "IN_PERSON")
    private String channel;

    public String getPractitionerId() { return practitionerId; }
    public void setPractitionerId(String practitionerId) { this.practitionerId = practitionerId; }

    public String getSpecialty() { return specialty; }
    public void setSpecialty(String specialty) { this.specialty = specialty; }

    public OffsetDateTime getStartTime() { return startTime; }
    public void setStartTime(OffsetDateTime startTime) { this.startTime = startTime; }

    public String getPatientId() { return patientId; }
    public void setPatientId(String patientId) { this.patientId = patientId; }

    public String getChannel() { return channel; }
    public void setChannel(String channel) { this.channel = channel; }
}
