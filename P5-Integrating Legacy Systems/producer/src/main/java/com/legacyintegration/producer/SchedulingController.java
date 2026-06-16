package com.legacyintegration.producer;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/v1")
public class SchedulingController {

    @GetMapping("/appointments/{id}")
    public ResponseEntity<Appointment> getAppointment(@PathVariable("id") String appointmentId) {
        Appointment appointment = new Appointment(
                appointmentId,
                "Dr. Smith",
                "2026-06-20T10:00:00"
        );
        return ResponseEntity.ok(appointment);
    }
}
