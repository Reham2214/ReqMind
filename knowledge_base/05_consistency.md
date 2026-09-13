# Requirement Consistency

## Definition

Requirements are consistent when they do not contradict each other and use compatible terminology, assumptions, constraints, and expected behaviors.

Consistency must often be evaluated across multiple requirements.

## Example

R001:
"The system shall retain transaction records for 30 days."

R002:
"The system shall retain transaction records for 90 days."

If both requirements apply to the same transaction records and context, they are inconsistent.

## Detection

To detect inconsistency:

1. Identify requirements referring to the same entity or behavior.
2. Compare their constraints and expected outcomes.
3. Check whether terminology is used consistently.
4. Check whether numerical values or rules disagree.
5. Determine whether the difference is a true contradiction or simply applies to different contexts.

## Important

Two requirements with different values are not automatically inconsistent.

Context must be considered.

Example:

R001:
"Free users may upload files up to 100 MB."

R002:
"Premium users may upload files up to 500 MB."

These requirements are consistent because they apply to different user categories.