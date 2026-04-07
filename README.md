# Sentra

Execution, governed.

Most systems act on incomplete or local truth.

Sentra determines whether execution is allowed before it happens.

Execution is no longer a default outcome. It is a goverened decision.

---

## Demo

A short walkthrough of the control model across core scenarios:

- recovery validation over time  
- dependency blocking  
- control transformation  
- policy toggle behavior  
- cross-system governance  
- safe-to-act propagation  

[Watch the demo]([https://drive.google.com/file/d/14ZbOMe-5fshb2oE9GBu6q9hUUOjO_6bW/view?usp=sharing](https://drive.google.com/file/d/1H_wzcya6eXz_0bccTd8DrJ8LVjhjECAX/view?usp=sharing)) (~5 min)

---

## What this demonstrates

- Recovery is not trusted immediately
- Dependencies influence execution decisions
- Actions can be reduced, not just allowed or blocked
- External requests are governed before execution
- Failures propagate across the system

---

## Why this matters

Most systems monitor events and react locally.

Sentra introduces a control layer between decision and execution, ensuring systems act only when it is actually safe to do so.

---

## What this is not

- Not monitoring
- Not alerting
- Not orchestration

This is a control layer that governs execution itself.

---

## Notes

This repository is a focused demonstration of the Sentra control model.
A production-oriented implementation is maintained separately.
