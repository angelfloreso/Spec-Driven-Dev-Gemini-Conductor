package com.legacyintegration.producer;

import com.fasterxml.jackson.annotation.JsonProperty;

public class Appointment {
    @JsonProperty("appointmentId")
    private String appointmentId;
    
    @JsonProperty("practitionerName")
    private String practitionerName;
    
    @JsonProperty("startTime")
    private String startTime;

    public Appointment(String appointmentId, String practitionerName, String startTime) {
        this.appointmentId = appointmentId;
        this.practitionerName = practitionerName;
        this.startTime = startTime;
    }

    public String getAppointmentId() {
        return appointmentId;
    }

    public String getPractitionerName() {
        return practitionerName;
    }

    public String getStartTime() {
        return startTime;
    }
}
