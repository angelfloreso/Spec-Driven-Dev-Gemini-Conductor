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
    public ResponseEntity<Void> registerPatient(PatientRegistration patientRegistration) {
        return ResponseEntity.status(HttpStatus.CREATED).build();
    }
}
