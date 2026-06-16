package com.specdrivendev.p6.model;

import io.swagger.v3.oas.annotations.media.Schema;

import java.time.OffsetDateTime;

@Schema(description = "Full appointment record returned by the API")
public class AppointmentDetails {

    @Schema(description = "Unique appointment identifier", example = "APT-001")
    private String appointmentId;

    @Schema(description = "Practitioner ID", example = "PRAC-001")
    private String practitionerId;

    @Schema(description = "Patient ID", example = "PAT-1001")
    private String patientId;

    @Schema(description = "Medical specialty", example = "General Medicine")
    private String specialty;

    @Schema(description = "Appointment start time")
    private OffsetDateTime startTime;

    @Schema(description = "Current status", allowableValues = {"BOOKED", "CHECKED_IN", "WITH_DOCTOR", "DISCHARGED", "CANCELLED", "COMPLETED"})
    private String status;

    @Schema(description = "Channel", allowableValues = {"IN_PERSON", "VIRTUAL"})
    private String channel;

    public String getAppointmentId() { return appointmentId; }
    public void setAppointmentId(String appointmentId) { this.appointmentId = appointmentId; }

    public String getPractitionerId() { return practitionerId; }
    public void setPractitionerId(String practitionerId) { this.practitionerId = practitionerId; }

    public String getPatientId() { return patientId; }
    public void setPatientId(String patientId) { this.patientId = patientId; }

    public String getSpecialty() { return specialty; }
    public void setSpecialty(String specialty) { this.specialty = specialty; }

    public OffsetDateTime getStartTime() { return startTime; }
    public void setStartTime(OffsetDateTime startTime) { this.startTime = startTime; }

    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }

    public String getChannel() { return channel; }
    public void setChannel(String channel) { this.channel = channel; }
}
