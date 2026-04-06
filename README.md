# Sentra

Execution, governed.

## Demo

Sentra determines whether systems are allowed to act before execution, based on time, dependencies, and system-wide conditions.

## What this shows

- Recovery is not trusted immediately
- Dependencies influence execution decisions
- Actions can be reduced, not just allowed or blocked
- External requests are governed before execution
- Failures propagate across the system

## Scenarios

1. Recovery Validation
2. Dependency Blocking
3. Control Transformation
4. Policy Toggle Effect
5. Cross-System Governance
6. Safe-to-Act Propagation

## Run locally

Start the API:

```bash
python3 gate_api.py
```

## Why this matters

Most systems monitor events and react locally.

Sentra introduces a control layer that determines whether execution should occur at all.
