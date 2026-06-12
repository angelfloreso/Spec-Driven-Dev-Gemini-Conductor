package com.immutablebuild.demo.service;

import com.immutablebuild.demo.api.model.NextAppointmentResponse;
import java.time.LocalDate;
import org.springframework.stereotype.Service;

@Service
public class SchedulingService {

    public NextAppointmentResponse findNextAppointment(Integer patientId) {
        NextAppointmentResponse response = new NextAppointmentResponse();
        response.setPatientId(patientId);
        response.setPractitioner("Dr. Alice Gray");
        response.setAppointmentDate(LocalDate.now().plusDays(3));
        return response;
    }
}
