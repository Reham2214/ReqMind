# Requirement Duplication

## Definition

Duplication occurs when two requirements express the same or substantially overlapping system behavior.

## Example

R001:
"The system shall allow users to reset their password."

R002:
"The system shall provide users with the ability to change a forgotten password."

These requirements may describe substantially the same functionality.

## Detection

To detect duplication:

1. Compare the main subject.
2. Compare the action.
3. Compare the object.
4. Compare conditions and constraints.
5. Determine whether both requirements introduce distinct behavior.

## Important

Similar wording does not automatically mean duplication.

Two requirements may discuss the same feature but impose different constraints.

Example:

R001:
"The system shall allow users to upload files."

R002:
"The system shall allow administrators to upload files up to 500 MB."

These are related, but they are not necessarily duplicates because R002 adds a specific constraint and actor.

## Recommendation

When duplication is detected, ReqMind may recommend:

- merging the requirements
- removing the redundant requirement
- clarifying the difference between them