package com.immutablebuild.demo;

import static io.restassured.RestAssured.given;

import com.atlassian.oai.validator.restassured.OpenApiValidationFilter;
import io.restassured.RestAssured;
import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.web.server.LocalServerPort;

@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
class ApiContractTest {

    @LocalServerPort
    int port;

    @Test
    void endpointResponseMatchesCurrentOpenApiSpec() {
        RestAssured.baseURI = "http://localhost";
        RestAssured.port = port;

        OpenApiValidationFilter contract =
                new OpenApiValidationFilter("src/main/resources/openapi/api-spec.yaml");

        given()
                .filter(contract)
                .queryParam("patientId", 101)
        .when()
                .get("/api/appointments/next")
        .then()
                .statusCode(200);
    }
}
