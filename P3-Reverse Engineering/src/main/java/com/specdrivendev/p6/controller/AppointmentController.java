package com.specdrivendev.p6.controller;

import com.specdrivendev.p6.model.AppointmentDetails;
import com.specdrivendev.p6.model.AppointmentRequest;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.media.Content;
import io.swagger.v3.oas.annotations.media.Schema;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.time.OffsetDateTime;
import java.util.Map;

@RestController
@RequestMapping("/appointments")
@Tag(name = "appointments", description = "Booking engine – slot holding, cancellation, and rescheduling (FR-02)")
public class AppointmentController {

    @Operation(
        summary = "Book an appointment (FR-02.1)",
        description = "Books a slot and locks it for 5 minutes to prevent double-booking. Returns 423 if the slot is already locked."
    )
    @ApiResponses({
        @ApiResponse(responseCode = "201", description = "Appointment booked successfully",
            content = @Content(schema = @Schema(implementation = Map.class))),
        @ApiResponse(responseCode = "400", description = "Validation error", content = @Content),
        @ApiResponse(responseCode = "423", description = "Slot locked or unavailable", content = @Content)
    })
    @PostMapping
    public ResponseEntity<Map<String, String>> bookAppointment(@Valid @RequestBody AppointmentRequest body) {
        String appointmentId = "APT-" + System.currentTimeMillis();
        return ResponseEntity.status(HttpStatus.CREATED).body(Map.of("appointmentId", appointmentId));
    }

    @Operation(
        summary = "Get appointment details (FR-02.5)",
        description = "Returns the full record for an appointment including current status."
    )
    @ApiResponses({
        @ApiResponse(responseCode = "200", description = "Appointment found",
            content = @Content(schema = @Schema(implementation = AppointmentDetails.class))),
        @ApiResponse(responseCode = "404", description = "Appointment not found", content = @Content)
    })
    @GetMapping("/{appointmentId}")
    public ResponseEntity<AppointmentDetails> getAppointment(
            @Parameter(description = "Unique appointment ID", example = "APT-001")
            @PathVariable String appointmentId) {
        AppointmentDetails details = new AppointmentDetails();
        details.setAppointmentId(appointmentId);
        details.setPractitionerId("PRAC-001");
        details.setSpecialty("General Medicine");
        details.setStartTime(OffsetDateTime.parse("2026-07-01T10:00:00Z"));
        details.setStatus("BOOKED");
        details.setChannel("IN_PERSON");
        return ResponseEntity.ok(details);
    }

    @Operation(
        summary = "Cancel an appointment (FR-02.3)",
        description = "Cancels the appointment and immediately releases the slot."
    )
    @ApiResponses({
        @ApiResponse(responseCode = "200", description = "Appointment cancelled, slot released"),
        @ApiResponse(responseCode = "404", description = "Appointment not found", content = @Content),
        @ApiResponse(responseCode = "409", description = "Appointment already cancelled or completed", content = @Content)
    })
    @PostMapping("/{appointmentId}/cancel")
    public ResponseEntity<Void> cancelAppointment(
            @Parameter(description = "Unique appointment ID", example = "APT-001")
            @PathVariable String appointmentId) {
        return ResponseEntity.ok().build();
    }
}
