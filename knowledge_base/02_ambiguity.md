# Requirement Ambiguity

## Definition

Ambiguity occurs when a requirement can reasonably be interpreted in more than one way.

Ambiguous requirements may cause different stakeholders, developers, or testers to understand different expected behaviors.

## Common Causes

Ambiguity may result from:

- vague words
- subjective adjectives
- unclear references
- unclear conditions
- undefined terminology
- words with multiple possible meanings

## Common Ambiguous Terms

Examples include:

- quickly
- easy
- simple
- user-friendly
- efficient
- reasonable
- adequate
- appropriate
- minimal
- maximum
- optimal
- modern
- convenient
- sufficient

## Example

Requirement:

"The system shall respond quickly."

Problem:

The word "quickly" has no defined threshold.

Different users may interpret it as:

- less than 1 second
- less than 2 seconds
- less than 5 seconds

Therefore the requirement is ambiguous.

## Improved Requirement

"The system shall respond to user requests within 2 seconds under normal operating conditions."

## Detection Guidance

When analyzing a requirement:

1. Identify vague or subjective terminology.
2. Determine whether the term has an objective definition.
3. Check whether different reasonable readers could interpret the requirement differently.
4. If the main issue is vague wording, classify the issue as Ambiguity.

## Distinction from Non-Verifiability

Ambiguity focuses on multiple possible interpretations.

Non-verifiability focuses on the inability to objectively determine whether the requirement has been satisfied.

A requirement may be both ambiguous and non-verifiable.

For the ReqMind classification scheme:

- Use Ambiguity when vague or subjective wording is the primary problem.
- Use Non-verifiable when the wording is relatively clear but no objective pass/fail criterion exists.