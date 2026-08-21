# General Reasoning Baseline (GRB)

**Status:** Research Artifact

## Purpose

This document establishes the General Reasoning Baseline (GRB): the observable behavior of a capable general-purpose LLM when asked to reason over an investment packet without CHOIR alignment.

The baseline exists to serve as a control group.

It captures what a competent LLM naturally externalizes when constrained to expose its working state. Future CHOIR-aligned behavior should be compared against this baseline rather than against hidden internal reasoning.

## Cause

During architecture development, we asked a simple question:

> If a general LLM with no knowledge of YUKTI were handed only an investment packet, what would it produce before learning CHOIR?

The answer became the General Reasoning Baseline.

This is not CHOIR behavior.

This is the closest approximation of disciplined reasoning that emerges before constitutional semantics are introduced.

## Baseline Execution

The baseline follows a simple progression.

Document

↓

Working State

↓

Object Graph

↓

Judgment

↓

Output

The important distinction is that the intermediate state becomes visible instead of remaining inside hidden model activations.

## Baseline Artifacts

A competent general-purpose model naturally produces the following artifacts.

| Artifact           | Purpose                                               |
| ------------------ | ----------------------------------------------------- |
| Orientation State  | Stabilizes local context before reasoning.            |
| Entity Graph       | Tracks people, companies, metrics, and references.    |
| Typed Objects      | Separates claims, evidence, assumptions, and metrics. |
| Dependency Graph   | Connects conclusions to supporting objects.           |
| Missing Basis List | Identifies absent supporting material.                |
| Judgment           | Produces a final recommendation or uncertainty state. |

These artifacts are descriptive observations, not constitutional primitives.

## Example Baseline Output

Given an investment packet, a baseline model may externalize something resembling:

* Decision context (if available)
* Document inventory
* Entity relationships
* Evidence vs. claims
* Missing supporting material
* Final judgment

Example outcomes include:

* INVEST
* DO NOT INVEST
* REVIEW REQUIRED
* INSUFFICIENT BASIS

## Relationship to CHOIR

GRB is intentionally limited.

It does not establish constitutional meaning.

Instead, it provides a comparison point.

| General Reasoning Baseline | CHOIR-Aligned                |
| -------------------------- | ---------------------------- |
| Working State              | Institutional State          |
| Entity                     | Reasoning Object             |
| Missing Basis              | Constitutional Basis Failure |
| Dependency                 | Provenance Dependency        |
| Judgment                   | Canonical Judgment           |
| Object Graph               | Institutional Graph          |

The structural flow remains similar.

The semantic guarantees change.

## Research Use

The General Reasoning Baseline exists for comparison.

Future CHOIR implementations should be evaluated by running identical reasoning tasks through both systems and observing which institutional behaviors emerge only after CHOIR alignment.

This document intentionally makes no claim that the baseline is correct.

It simply records the behavior of a competent general-purpose reasoning model before constitutional semantics are applied.