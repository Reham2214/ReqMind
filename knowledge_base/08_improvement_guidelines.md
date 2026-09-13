# Requirement Improvement Guidelines

## General Rule

An improved requirement should preserve the original intent while removing the detected quality issue.

Do not introduce unrelated functionality.

## Ambiguity

Replace vague language with measurable or explicit criteria.

Weak:

"The system shall respond quickly."

Improved:

"The system shall respond within 2 seconds."

## Incompleteness

Add missing information required for implementation or verification.

Weak:

"The system shall send notifications."

Improved:

"When a payment fails, the system shall send an email notification to the account owner within 30 seconds."

## Non-Verifiability

Add an objective acceptance criterion.

Weak:

"The system shall be user-friendly."

Improved:

"At least 80% of representative users shall complete the checkout task without assistance during usability testing."

## Conflict

Do not arbitrarily select one requirement as correct.

Instead:

- identify the conflicting requirements
- explain the contradiction
- recommend clarification
- suggest a possible resolution only when sufficient context exists

## Duplication

Recommend merging or removing redundant requirements while preserving distinct constraints.

## No Issue

If no significant issue is detected:

- do not invent a problem
- preserve the requirement
- explain that no quality issue was identified