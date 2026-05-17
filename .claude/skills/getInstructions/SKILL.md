---
name: getInstructions
description: Read a file once (PDF, image, DOCX, etc.) and extract a detailed structured summary of its instructions — steps, requirements, visual examples, constraints, and grading criteria — saved to extracted/instructions/<name>.md for token-efficient future reference.
version: 1.0
---

Read the specified file and extract all instructional content into a structured markdown file saved to `extracted/instructions/`.

## Instructions

1. **Resolve the file path.** Accept a bare filename (e.g., `lab9.pdf`) or a relative path. Derive the output filename by stripping the extension: `lab9.pdf` → `extracted/instructions/lab9.md`. Create `extracted/instructions/` if it doesn't exist.

2. **Read the file** using the Read tool. Read all pages in full — do not summarize early or skip sections.

3. **Handle embedded images and screenshots.** First assess whether the assignment is UI/visual in nature (e.g., web development, UI design, front-end styling). Then:

   - **If UI/visual assignment:** For each image, produce a dedicated Visual Example block with enough detail to write the CSS directly. Include:
     - **Page background:** exact color or gradient (include full CSS value if visible)
     - **Layout method:** how content is centered or positioned (flexbox, margin auto, text-align center, etc.) — infer from the visual if not stated
     - **Container structure:** is the content inside a box/card, or do elements float directly on the background?
     - **Each text element:** font size (estimate in px), font weight, color, alignment
     - **Each UI element** (table, form, button, input, select, error message): background color, border (width, style, color), padding estimate, width, alignment on page
     - **Table specifics:** border-collapse, header style, whether border is on `tr` or `td` (critical difference — `tr` border applies to the whole row as a line, `td` border applies per cell), hover state color, whether rows have explicit background or rely on nth-child alternating
     - **Form specifics:** how labels and inputs are aligned, whether form is centered as a block
     - **Error message:** exact text, color, font weight, size, position relative to other elements
     - **Button:** background, border, text color, padding, position (centered? left?)
     - **Any visible state:** hover, active, error, empty — describe what changes visually

   - **If non-visual assignment** (algorithms, math, theory, etc.): Extract only the informational content from images (diagrams, pseudocode, graph examples, data structures). Skip color/font/layout descriptions — they are irrelevant.

4. **Write `extracted/instructions/<name>.md`** with these sections (omit empty ones):

   ### Overview
   One paragraph: what the assignment is and its main goal.

   ### Tasks
   Numbered list of all steps/deliverables. Use verbatim wording from the source where possible.

   ### Requirements & Constraints
   Bullet list of hard requirements, technical constraints, and "must"/"do not" rules.

   ### Visual Examples
   One subsection per screenshot/image. Title each after the UI element it depicts (e.g., `#### Login Page`). Use the description format from step 3.

   ### Grading Criteria
   Point values and rubric items exactly as written. Preserve original structure.

   ### Submission
   What to submit, where, and by when.

   ### Notes
   Warnings, hints, clarifications, or edge cases outside the main task sections.

5. **Confirm.** After writing, output: `Saved to extracted/instructions/<name>.md`

## Usage

```
/getInstructions lab9.pdf
/getInstructions "Lab 09.pdf"
/getInstructions path/to/lab9.pdf
```
