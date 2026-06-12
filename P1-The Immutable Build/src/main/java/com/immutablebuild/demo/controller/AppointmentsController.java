package com.immutablebuild.demo.controller;

import com.immutablebuild.demo.api.AppointmentsApi;
import com.immutablebuild.demo.api.model.NextAppointmentResponse;
import com.immutablebuild.demo.service.SchedulingService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class AppointmentsController implements AppointmentsApi {

    private final SchedulingService schedulingService;

    public AppointmentsController(SchedulingService schedulingService) {
        this.schedulingService = schedulingService;
    }

    @Override
    public ResponseEntity<NextAppointmentResponse> getNextAppointment(Integer patientId) {
        NextAppointmentResponse response = schedulingService.findNextAppointment(patientId);
        return ResponseEntity.ok(response);
    }
}
