package com.specdrivendev.p6.config;

import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.Contact;
import io.swagger.v3.oas.models.info.Info;
import io.swagger.v3.oas.models.info.License;
import io.swagger.v3.oas.models.servers.Server;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import java.util.List;

@Configuration
public class OpenApiConfig {

    @Bean
    public OpenAPI medSchedOpenAPI() {
        return new OpenAPI()
                .info(new Info()
                        .title("MedSched API")
                        .description("Reverse-engineered OpenAPI spec from Spring Boot annotations. Practice project for P6.")
                        .version("1.0.0")
                        .contact(new Contact()
                                .name("Technical Lead Practice")
                                .email("support@medsched.example.com"))
                        .license(new License()
                                .name("MIT")))
                .servers(List.of(
                        new Server().url("http://localhost:8080").description("Local dev server")
                ));
    }
}
