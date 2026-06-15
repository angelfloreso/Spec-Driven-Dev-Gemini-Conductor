package com.legacyintegration.consumer;

import com.google.gson.Gson;
import com.google.gson.JsonObject;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.web.client.RestTemplateBuilder;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

@Service
public class SchedulingClient {

    private final RestTemplate restTemplate;
    private final String producerUrl;

    public SchedulingClient(RestTemplateBuilder builder, 
                           @Value("${producer.url:http://localhost:8080}") String producerUrl) {
        this.restTemplate = builder.build();
        this.producerUrl = producerUrl;
    }

    public AppointmentDTO getAppointment(String appointmentId) {
        String url = producerUrl + "/api/v1/appointments/" + appointmentId;
        String response = restTemplate.getForObject(url, String.class);
        
        Gson gson = new Gson();
        JsonObject jsonObject = gson.fromJson(response, JsonObject.class);
        
        AppointmentDTO dto = new AppointmentDTO();
        dto.appointmentId = jsonObject.get("appointmentId").getAsString();
        dto.practitionerName = jsonObject.get("practitionerName").getAsString();
        dto.startTime = jsonObject.get("startTime").getAsString();
        
        return dto;
    }

    public static class AppointmentDTO {
        public String appointmentId;
        public String practitionerName;
        public String startTime;

        @Override
        public String toString() {
            return "AppointmentDTO{" +
                    "appointmentId='" + appointmentId + '\'' +
                    ", practitionerName='" + practitionerName + '\'' +
                    ", startTime='" + startTime + '\'' +
                    '}';
        }
    }
}
