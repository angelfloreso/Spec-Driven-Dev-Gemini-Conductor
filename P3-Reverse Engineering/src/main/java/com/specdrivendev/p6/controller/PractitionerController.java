package com.specdrivendev.p6.controller;

import com.specdrivendev.p6.model.AppointmentDetails;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * EXERCISE CONTROLLER - intentionally missing springdoc annotations.
 *
 * The tutorial asks you to add @Tag, @Operation, @ApiResponses, and @Parameter
 * to make this controller fully documented in the generated OpenAPI spec.
 *
 * See README.md Step 6 for instructions.
 */
@RestController
@RequestMapping("/practitioners")
public class PractitionerController {

    @GetMapping("/{practitionerId}/queue")
    public ResponseEntity<List<AppointmentDetails>> getQueue(
            @PathVariable String practitionerId) {
        return ResponseEntity.ok(List.of());
    }

    @PostMapping("/{practitionerId}/schedule-blocks")
    public ResponseEntity<Void> blockSchedule(
            @PathVariable String practitionerId,
            @RequestBody Object body) {
        return ResponseEntity.status(201).build();
    }
}
