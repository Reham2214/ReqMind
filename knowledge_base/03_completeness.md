# Requirement Completeness

## Definition

A requirement is complete when it contains sufficient information to understand, implement, and verify the required behavior.

## Common Missing Information

A requirement may be incomplete when it does not specify one or more of:

- actor
- action
- object
- trigger
- condition
- input
- output
- timing
- frequency
- threshold
- unit
- scope
- exception
- expected response

## Example

"The system shall send an email."

Missing information may include:

- who receives the email
- when the email is sent
- what triggers the email
- what the email contains

## Improved Requirement

"When a user resets their password, the system shall send a password-reset email to the email address registered to the user's account within 30 seconds."

This version defines:

- trigger
- actor/system
- action
- recipient
- timing

## Detection Guidance

When analyzing a requirement:

1. Identify the expected behavior.
2. Determine whether the trigger or condition is specified.
3. Determine whether the expected result is sufficiently defined.
4. Check for missing constraints or acceptance criteria.
5. If important information is missing, classify the requirement as Incompleteness.

## Important Distinction

Do not classify every short requirement as incomplete.

A short requirement can still be complete if its meaning and verification criteria are sufficiently clear within the available context.