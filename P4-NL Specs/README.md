# P4 Tutorial - From Natural Language Specs to OpenAPI YAML

This practice teaches how to convert a real Functional Requirements Document (FRD) into a machine-readable OpenAPI 3.0 YAML spec using AI assistance.

## The Core Idea

Natural language documents (PDFs, Word docs, Confluence pages) hold the intent of a system, but they cannot be executed or validated by machines.

Spec-Driven Development starts by extracting that intent into a precise, versioned OpenAPI spec before writing any code. This tutorial shows you how to do that step.

---

## What You Will Learn

1. How to read a requirements document and identify API operations.
2. How to craft a prompt that produces a well-structured OpenAPI YAML from a PDF.
3. How to validate that the generated YAML correctly represents the requirements.
4. What to look for in the YAML before it becomes the source of truth for your build.

---

## The Requirements Document

The PDF in this folder is the **MedSched Functional Requirements Document**.

```
P4-NL Specs/Functional_Requirements_Document_MedSched.pdf
```

It defines four functional requirement areas:

| ID | Area |
|----|------|
| FR-01 | Patient onboarding and de-duplication |
| FR-02 | Booking engine, slot locking, availability, cancellation, rescheduling, calendar blocks |
| FR-03 | Notifications and reminder dispatch |
| FR-04 | Waiting room, lifecycle tracking, and practitioner queue |

---

## Step 1 - Read the Document

Open `Functional_Requirements_Document_MedSched.pdf` and note:

- What entities exist? (Patient, Appointment, Practitioner, Block...)
- What operations are described? (register, book, cancel, notify, queue...)
- What constraints are mentioned? (de-duplication, slot lock, RBAC roles...)
- What data fields appear? (fullName, dob, startTime, status...)

This reading shapes the prompt you will write in the next step.

---

## Step 2 - Use This Prompt With an AI Assistant

Copy the prompt below into Gemini, ChatGPT, Claude, or any LLM capable of reading PDFs.

If your AI assistant supports file uploads, attach the PDF directly. Otherwise, paste the text content of the document alongside the prompt.

---

### Prompt: Generate OpenAPI YAML From Requirements Document

```
You are a senior API architect helping to apply Spec-Driven Development.

I am attaching a Functional Requirements Document for a Medical Appointment Management System called MedSched.

Your task is to analyze the document and produce a complete, valid OpenAPI 3.0.3 YAML specification that satisfies all documented functional requirements.

Follow these rules:
1. Use operationId values that match the functional requirement IDs where possible (e.g., registerPatient for FR-01.1).
2. For each endpoint, document all meaningful HTTP response codes described or implied in the requirements (e.g., 201, 400, 404, 409, 423).
3. Define all request body schemas and response schemas in the components/schemas section with required fields explicitly listed.
4. Use snake_case for path segments and camelCase for schema property names.
5. Mark fields as required only if the requirement explicitly states they are mandatory.
6. Add a short description to each endpoint that references the functional requirement it satisfies.
7. Use enum values for fields with a fixed set of allowed values (e.g., status, sex, channel).
8. Format date/time fields with format: date-time or format: date.

Output only the YAML. No prose before or after. Begin with:

openapi: 3.0.3
info:
  title: MedSched API
  version: 1.0.0
```

---

## Step 3 - Save The Generated YAML

Once the AI returns the YAML, save it to this folder:

```bash
cp ~/Downloads/your-generated-spec.yaml \
  "/root/projects/SpecDrivenDev-Conductor/P4-NL Specs/medsched-generated.yaml"
```

Then open it in VS Code to review it visually.

You can also validate it immediately with an online linter:
- https://editor.swagger.io (paste YAML, errors appear on the right)
- https://redocly.com/tools/openapi-linter

---

## Step 4 - Compare Against The Reference Spec

A reference YAML built from the same document is provided in this folder:

```
P4-NL Specs/medsched-reference.yaml
```

Compare your generated spec with the reference:

```bash
diff medsched-generated.yaml medsched-reference.yaml
```

The reference covers all four FR areas. Use it to spot gaps in your generated output.

---

## Step 5 - Developer Validation Checklist

After generating the YAML, work through this checklist before treating it as a source of truth.

### FR Coverage

- [ ] FR-01: Is there a POST /patients endpoint for patient registration?
- [ ] FR-01: Does PatientRegistration schema include govtIdToken for de-duplication?
- [ ] FR-02: Is there a POST /appointments endpoint for booking?
- [ ] FR-02: Does the booking endpoint document 423 (slot locked) as a response?
- [ ] FR-02: Is there a POST /appointments/{id}/cancel endpoint?
- [ ] FR-02: Is there a POST /appointments/{id}/reschedule endpoint?
- [ ] FR-02: Is there an endpoint for calendar blocks (schedule-blocks)?
- [ ] FR-03: Is there a POST /reminders/dispatch endpoint?
- [ ] FR-03: Is there a GET /reminders/ack/{token} endpoint for acknowledgements?
- [ ] FR-04: Is there a POST /appointments/{id}/status endpoint for lifecycle transitions?
- [ ] FR-04: Is there a GET /practitioners/{id}/queue endpoint for the waiting room view?

### Schema Quality

- [ ] All required fields are explicitly declared in `required:` arrays.
- [ ] Date/time fields use `format: date-time` or `format: date`.
- [ ] Enum values are defined for: status (BOOKED, CANCELLED, COMPLETED), sex (M, F, Other).
- [ ] Response schemas are defined in components/schemas, not inline.
- [ ] Schemas use camelCase property names consistently.

### HTTP Semantics

- [ ] Creation endpoints return 201, not 200.
- [ ] Not-found cases return 404.
- [ ] Conflict cases (duplicate patient) return 409.
- [ ] Locked slots return 423.
- [ ] Read-only GET endpoints do not have request bodies.

### OpenAPI Structural Rules

- [ ] `openapi: 3.0.3` header is present.
- [ ] All `$ref` values point to existing components.
- [ ] `operationId` values are unique across all paths.
- [ ] At least one server URL is defined.
- [ ] The spec validates cleanly at https://editor.swagger.io.

---

## Step 6 - Improve The Prompt (Iteration Exercise)

If your generated YAML was missing items from the checklist, refine your prompt and regenerate.

Common improvements:
- Add "Include reminders and acknowledgement endpoints from FR-03."
- Add "Include lifecycle status transition endpoint from FR-04."
- Add "Each schema must include a description for every property."

This is the real lesson: **prompt quality determines spec quality. Spec quality determines code quality.**

---

## Key Takeaway

Natural language requirements → AI-assisted spec extraction → OpenAPI YAML → machine-enforced contract.

No step of the implementation should happen before the YAML spec is reviewed, validated, and committed.
