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
