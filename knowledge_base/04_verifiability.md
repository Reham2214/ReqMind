# Requirement Verifiability

## Definition

A requirement is verifiable when objective evidence can determine whether the requirement has been satisfied.

Verification may involve:

- testing
- inspection
- demonstration
- analysis

## Non-Verifiable Language

Examples include:

- user-friendly
- attractive
- highly secure
- easy to use
- efficient
- fast
- reliable
- intuitive
- convenient

These terms require objective criteria.

## Example

"The system shall be user-friendly."

Problem:

There is no objective pass/fail criterion.

Improved:

"At least 80% of representative users shall complete the defined checkout task without assistance during usability testing."

## Detection Guidance

Classify a requirement as Non-verifiable when:

- the requirement is reasonably understandable,
- but no objective criterion exists to determine whether it has been satisfied.

## Difference from Ambiguity

Ambiguity:

"The system shall respond quickly."

The term "quickly" has multiple possible interpretations.

Non-verifiable:

"The interface shall provide an excellent user experience."

The intended concept may be understandable, but "excellent" does not provide an objective pass/fail criterion.

For ReqMind:

- vague wording → Ambiguity
- clear concept but no objective verification method → Non-verifiable