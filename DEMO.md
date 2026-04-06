# Demo Guide

## What this demo shows

Sentra determines whether systems are allowed to act before execution.

## Scenarios

### 1. Recovery Validation
Recovery is not trusted immediately. Stability must be proven over time.

### 2. Dependency Blocking
A locally stable service can still be blocked when a dependency is degraded.

### 3. Control Transformation
A preferred action can be reduced under degraded system conditions.

### 4. Policy Toggle Effect
The same preferred action can produce different outcomes depending on active policy.

### 5. Cross-System Governance
External execution requests are still governed by system-wide conditions.

### 6. Safe-to-Act Propagation
Instability in one part of the system can restrict execution across multiple services.
