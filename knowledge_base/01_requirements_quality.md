# Software Requirements Quality

## Purpose

This document defines general quality characteristics for software requirements.

A high-quality requirement should be:

- Clear
- Unambiguous
- Complete
- Consistent
- Verifiable
- Feasible
- Necessary
- Traceable
- Testable
- Quantifiable when appropriate

## Clear Requirements

A requirement should clearly describe the expected system behavior, constraint, or quality attribute.

Avoid vague language that allows multiple interpretations.

Examples of vague terms include:

- quickly
- easy
- user-friendly
- efficient
- reasonable
- adequate
- modern
- simple
- appropriate
- as soon as possible

## Unambiguous Requirements

A requirement is unambiguous when different readers are likely to interpret it in the same way.

Ambiguity commonly occurs when subjective or vague terminology is used.

Example:

"The system shall respond quickly."

The word "quickly" does not define a measurable response time.

Better:

"The system shall respond within 2 seconds."

## Complete Requirements

A requirement should contain enough information for developers and testers to understand what must be implemented and how compliance can be determined.

Missing information may include:

- actor
- trigger
- condition
- input
- output
- timing
- threshold
- unit
- scope
- exception behavior
- expected system response

Example:

"The system shall send notifications."

This may be incomplete because it does not specify:

- who receives the notification
- when it is sent
- what triggers it
- which notification channel is used
- what information it contains

## Consistent Requirements

Requirements should not contradict or use conflicting definitions.

Example:

Requirement R001:
"The system shall retain user data for 30 days."

Requirement R002:
"The system shall retain user data for 90 days."

If both requirements apply to the same data and context, they are inconsistent or conflicting.

## Verifiable Requirements

A requirement should allow an objective test, inspection, demonstration, or analysis to determine whether it has been satisfied.

A requirement is difficult to verify when it uses subjective language without measurable criteria.

Example:

"The system shall be highly secure."

This does not define objective security criteria.

Better:

"The system shall lock the account after five consecutive failed login attempts."

## Measurable Requirements

When a quality attribute is required, measurable thresholds should be provided when possible.

Example:

Weak:

"The application shall load quickly."

Better:

"The application shall display the dashboard within 2 seconds under normal operating conditions."

## Testable Requirements

A requirement should provide enough information to create a test case.

A good requirement should allow a tester to determine:

- input
- condition
- expected behavior
- expected result
- acceptance criteria

## Good Requirement Example

"The system shall lock the user account for 15 minutes after five consecutive failed login attempts."

This requirement contains:

- system behavior
- trigger condition
- threshold
- duration
- measurable outcome

It is therefore relatively clear and testable.