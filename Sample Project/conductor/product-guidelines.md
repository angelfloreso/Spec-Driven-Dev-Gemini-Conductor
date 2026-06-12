# Product Guidelines - MedSched

## 1. Visual Brand & Theme
* **Theme:** Standard Clinical. Adopt a traditional, clinical white-and-blue interface that maximizes familiarity, readability, and trust.
* **Color Palette:**
  * **Primary Blue:** Clinical blue (e.g., `#0284c7` or `#1d4ed8`) for headers, primary actions, and branding.
  * **Neutrals:** Soft whites, light grays (`#f8fafc`, `#f1f5f9`), and clean dark grays (`#1e293b`) for text.
  * **Semantic Accents:** Clean green for success or availability, yellow/orange for transient holds or warnings, and soft red for cancellations/errors.
* **Typography:** Clean, highly legible sans-serif fonts (e.g., Inter, system-ui) to convey precision and professionalism.

## 2. Copywriting & Tone of Voice
* **Tone:** Empathetic & Professional. The system must communicate in a way that is reassuring, clear, and warm.
* **Prose Style:** Minimize clinical jargon or internal system jargon (e.g., prefer "We are reserving this time slot for you..." over "FR-02 Slot Lock Active").
* **Error/Validation Handling:** Provide helpful, actionable feedback instead of raw system exceptions.

## 3. User Experience & Layout Patterns
* **Workflow Design:** Step-by-Step Wizards. Complex processes should be split into manageable, sequential steps rather than overwhelming forms:
  * **Onboarding:** Step 1: Personal Info -> Step 2: Contact Details -> Step 3: Demographics/De-duplication Check -> Step 4: Complete.
  * **Booking:** Step 1: Select Practitioner -> Step 2: Pick Available Slot -> Step 3: Review & Lock Hold -> Step 4: Confirm.
* **Interface Density:** Generous padding and clear typography spacing to accommodate users of all ages and digital literacies.

## 4. Frontend Styling & Technical Standards
* **Styling Framework:** Tailwind CSS. Align all UI layouts and components using Tailwind utility classes.
* **Custom Configuration:** Customize `tailwind.config.js` to incorporate the clinical blue and semantic color tokens, avoiding the use of hardcoded, arbitrary Tailwind color values (e.g., use `bg-brand-blue` instead of `bg-blue-600` or `bg-[#1d4ed8]`).
* **Responsive Layout:** Ensure patient-facing wizards scale fluidly down to mobile sizes (375px+). Staff views should be optimized for desktop/tablet screens.
