package com.specdrivendev.p6.model;

import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;

import java.time.LocalDate;
import java.util.List;

@Schema(description = "Patient registration request")
public class PatientRegistration {

    @Schema(description = "Legal full name", example = "Alice Smith", requiredMode = Schema.RequiredMode.REQUIRED)
    @NotBlank
    private String fullName;

    @Schema(description = "Date of birth", example = "1990-05-14", requiredMode = Schema.RequiredMode.REQUIRED)
    @NotNull
    private LocalDate dob;

    @Schema(description = "Biological sex", allowableValues = {"M", "F", "Other"})
    private String sex;

    @Schema(description = "Contact phone number", example = "+1-555-0100", requiredMode = Schema.RequiredMode.REQUIRED)
    @NotBlank
    private String phone;

    @Schema(description = "Contact email address", example = "alice@example.com", requiredMode = Schema.RequiredMode.REQUIRED)
    @Email @NotBlank
    private String email;

    @Schema(description = "Government identity token for de-duplication (FR-01.2)", example = "GOV-ID-XYZ123")
    private String govtIdToken;

    @Schema(description = "Known allergies list")
    private List<String> allergies;

    public String getFullName() { return fullName; }
    public void setFullName(String fullName) { this.fullName = fullName; }

    public LocalDate getDob() { return dob; }
    public void setDob(LocalDate dob) { this.dob = dob; }

    public String getSex() { return sex; }
    public void setSex(String sex) { this.sex = sex; }

    public String getPhone() { return phone; }
    public void setPhone(String phone) { this.phone = phone; }

    public String getEmail() { return email; }
    public void setEmail(String email) { this.email = email; }

    public String getGovtIdToken() { return govtIdToken; }
    public void setGovtIdToken(String govtIdToken) { this.govtIdToken = govtIdToken; }

    public List<String> getAllergies() { return allergies; }
    public void setAllergies(List<String> allergies) { this.allergies = allergies; }
}
