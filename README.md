# SafeAgent

**A Research Framework for Reliable and Risk-Aware AI Agent Execution**

## Overview

SafeAgent is an open-source research project investigating reliable execution and recovery mechanisms for enterprise AI agents operating in state-changing workflows.

The project focuses on a fundamental reliability challenge: how should an autonomous system respond when an external operation may have succeeded, but its execution outcome is uncertain?

Such scenarios arise when API requests time out, network responses are lost, or execution processes fail after committing changes to external systems.

Unsafe retries can result in duplicate operations, inconsistent system states, and unintended business consequences.

## Research Objectives

SafeAgent aims to investigate:

1. Reliable recovery from uncertain tool-execution outcomes.
2. Prevention of duplicate state-changing operations.
3. Risk-aware decisions involving retries, verification, and human intervention.
4. Recovery behavior under simulated infrastructure failures.
5. Trade-offs between reliability, recovery latency, and execution overhead.

## Initial Research Environment

The initial experimental environment simulates an electricity utility service-request system.

A service request creates a ticket representing a customer-reported utility issue.

The baseline implementation intentionally lacks idempotency protection, allowing repeated operations to generate duplicate tickets.

This establishes a controlled environment for evaluating subsequent recovery mechanisms.

## Research Approach

The planned evaluation will compare:

* Naive execution and retry behavior.
* Idempotency-aware execution.
* Verification-based recovery.
* Risk-aware recovery policies.

Experiments will measure duplicate operations, recovery success, execution overhead, and other reliability metrics.

These comparisons are planned and have not yet been completed.

## Repository Structure

```text
src/safeagent/          Core implementation
experiments/baselines/  Baseline experiments
tests/                  Automated tests
docs/                   Architecture and methodology
```

## Installation

Requirements: Python 3.10+

```bash
python -m pip install -e ".[dev]"
```

## Run Baseline Experiment

```bash
python experiments/baselines/naive_retry.py
```

## Run Tests

```bash
python -m pytest -v
```

## Current Research Status

**Initial baseline implemented.**

The repository currently provides a deterministic, in-memory utility service simulation demonstrating duplicate ticket creation under repeated requests.

It does not yet contain an AI agent, network fault injection, or a validated risk-aware recovery mechanism.

## Reproducibility

The project is being developed with reproducibility as a core objective.

Source code, experiment configurations, automated tests, evaluation metrics, and documented results will be maintained as the research progresses.

## Research Scope

All utility service requests and customer identifiers used in the initial experiments are synthetic.

The framework is intended for research and experimentation, not production deployment or autonomous operation of critical infrastructure.
