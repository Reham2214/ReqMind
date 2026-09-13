# Requirement Conflicts

## Definition

A conflict occurs when two or more applicable requirements impose mutually incompatible behaviors, constraints, or values.

## Example

R001:
"The system shall allow files up to 500 MB."

R002:
"The system shall reject files larger than 100 MB."

If both apply to the same users and same upload operation, the requirements conflict.

## Conflict Detection

The analysis should:

1. Identify requirements referring to the same feature or entity.
2. Compare their expected behaviors.
3. Compare numerical constraints.
4. Check whether their conditions overlap.
5. Determine whether both requirements can be satisfied simultaneously.

## Context

Requirements may appear contradictory but actually be valid when their contexts differ.

Example:

R001:
"Administrators may upload files up to 500 MB."

R002:
"Regular users may upload files up to 100 MB."

These are not conflicting because the requirements apply to different actors.

## Evidence

When reporting a conflict, ReqMind should identify the related requirement IDs.

Example:

Issue Label:
Conflict

Evidence:
"R001 allows uploads up to 500 MB, while R002 limits uploads to 100 MB for the same context."

## Recommendation

When a conflict is detected, the system should recommend clarifying:

- applicable actor
- context
- priority
- threshold
- business rule
