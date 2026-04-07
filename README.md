# Sentra

Execution, governed.

Most systems act on incomplete or local truth.

Sentra determines whether systems are allowed to act before execution, based on system-wide state, dependencies, and time.

---

## Demo

Sentra governs whether systems are allowed to act before execution.

[Watch the demo]([https://drive.google.com/file/d/14ZbOMe-5fshb2oE9GBu6q9hUUOjO_6bW/view?usp=sharing](https://drive.google.com/file/d/1H_wzcya6eXz_0bccTd8DrJ8LVjhjECAX/view?usp=sharing)) (~5 min)

---

## What this shows

- Recovery is not trusted immediately
- Dependencies influence execution decisions
- Actions can be reduced, not just allowed or blocked
- External requests are governed before execution
- Failures propagate across the system

---

## Why this matters

Most systems monitor events and react locally.

Sentra introduces a control layer between decision and execution, ensuring systems only act when it is actually safe to do so.

---

## What this is not

- Not monitoring
- Not alerting
- Not orchestration

This is a control layer that governs execution itself.

---

## Demo scenarios

1. Recovery Validation
2. Dependency Blocking
3. Control Transformation
4. Policy Toggle Effect
5. Cross-System Governance
6. Safe-to-Act Propagation

---

## Notes

This repository is a public exploration surface for the Sentra demo and concept. Runnable implementation is maintained separately.

This introduces a new layer of control in modern systems.
