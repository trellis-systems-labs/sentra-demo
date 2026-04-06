CINEMATIC = True # toggle on/off
SHOW_INTERNALS = False # toggle on/off

import json
import urllib.request
from pathlib import Path
import time
import sys
import os

BASE_URL = "http://127.0.0.1:9007"
OUTPUT_LINES = []

RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
RED = "\033[31m"
YELLOW = "\033[33m"
GREEN = "\033[32m"
CYAN = "\033[36m"
MAGENTA = "\033[35m"

def wait(t=0.6):
    if CINEMATIC:
        time.sleep(t)

def log(line: str = ""):
    print(line)
    OUTPUT_LINES.append(line)

def type_line(text, delay=0.008):
    if not CINEMATIC:
        log(text)
        return
    for c in text:
        sys.stdout.write(c)
        sys.stdout.flush()
        time.sleep(delay)
    sys.stdout.write("\n")
    OUTPUT_LINES.append(text)

def beat(text, pause=0.8, delay=0.008):
    type_line(text, delay=delay)
    wait(pause)

def clear():
    if CINEMATIC:
        os.system("clear")

def color_state(state: str) -> str:
    if state == "UNSTABLE":
        return f"{RED}{state}{RESET}"
    if state == "DEGRADED":
        return f"{YELLOW}{state}{RESET}"
    if state == "STABLE":
        return f"{GREEN}{state}{RESET}"
    return state

def color_safe(safe: bool) -> str:
    return f"{GREEN}YES{RESET}" if safe else f"{RED}NO{RESET}"

def color_action(action: str) -> str:
    if action in ["escalate", "no_action"]:
        return f"{MAGENTA}{action}{RESET}"
    if action in ["observe", "limited_action"]:
        return f"{YELLOW}{action}{RESET}"
    if action == "proceed":
        return f"{GREEN}{action}{RESET}"
    return action

def header(title, purpose):
    clear()
    beat(f"\n{DIM}=============================={RESET}", 0.15)
    beat(f"{BOLD}{title}{RESET}", 0.15)
    beat(f"{DIM}=============================={RESET}", 0.35)
    beat(f"{CYAN}Purpose:{RESET} {purpose}", 0.9)

def baseline(text):
    beat(f"\n{BOLD}Without control:{RESET}", 0.3)
    beat(text, 0.8)
    beat(f"\n{BOLD}With Sentra:{RESET}", 0.6)

def save_output(filepath: str = "demo_output.txt"):
    Path(filepath).write_text("\n".join(OUTPUT_LINES) + "\n", encoding="utf-8")


def post(path: str, payload: dict | None = None):
    if payload is None:
        payload = {}

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"{BASE_URL}{path}",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))


def get(path: str):
    with urllib.request.urlopen(f"{BASE_URL}{path}") as resp:
        return json.loads(resp.read().decode("utf-8"))

def print_step(title, result):
    beat(f"\n{BOLD}{title}{RESET}", 0.2)

    state = result.get("state")
    safe_bool = bool(result.get("safe_to_act"))

    final_action = (
        result.get("final_action")
        or result.get("enforcement", {}).get("final_action")
    )
    preferred_action = (
        result.get("preferred_action")
        or result.get("decision", {}).get("preferred_action")
    )

    action = final_action or preferred_action or "unknown"

    beat(f"State: {color_state(state)}", 0.15)
    beat(f"Safe to act: {color_safe(safe_bool)}", 0.15)
    beat(f"Action: {color_action(action)}", 0.25)

    if state == "UNSTABLE":
        beat("→ System blocks unsafe execution", 0.7)
    elif state == "DEGRADED":
        if not safe_bool:
            beat("→ Recovery is not yet trusted", 0.7)
        else:
            beat("→ Limited operation allowed", 0.7)
    elif state == "STABLE":
        if not safe_bool:
            beat("→ Service blocked despite local stability", 1.1)
        elif action == "limited_action":
            beat("→ Action reduced due to degraded system state", 1.0)
        else:
            beat("→ Execution allowed", 0.7)

def assert_equal(name: str, actual, expected):
    if actual == expected:
        log(f"[PASS] {name}: expected={expected}, actual={actual}")
        return True
    else:
        log(f"[FAIL] {name}: expected={expected}, actual={actual}")
        return False


def reset_demo():
    result = post("/reset")
    if SHOW_INTERNALS:
        log(f"\n[reset] {result}")

def set_policy(policy_name: str, enabled: bool):
    result = post("/policy", {
        "policy_name": policy_name,
        "enabled": enabled,
    })
    if SHOW_INTERNALS:
        log(f"[policy] {result}")
    return result

def run_recovery_validation():
    clear()
    header(
        "SCENARIO 01 - RECOVERY VALIDATION",
        "Demonstrates that recovery must be proven over time before the system returns to STABLE."
    )
    baseline("A service recovers and is trusted immediately.")

    reset_demo()

    steps = [
        ("service-a fails", {
            "service_name": "service-a",
            "signal_type": "failure",
            "dependencies": [],
        }),
        ("service-a recovers", {
            "service_name": "service-a",
            "signal_type": "recovered",
            "dependencies": [],
        }),
        ("service-a stabilizing 1", {
            "service_name": "service-a",
            "signal_type": "stable",
            "dependencies": [],
        }),
        ("service-a stabilizing 2", {
            "service_name": "service-a",
            "signal_type": "stable",
            "dependencies": [],
        }),
        ("service-a stabilizing 3", {
            "service_name": "service-a",
            "signal_type": "stable",
            "dependencies": [],
        }),
    ]

    final_result = None
    for title, payload in steps:
        final_result = post("/evaluate", payload)

        if title == "service-a stabilizing 3":
            beat("→ Execution allowed only after stability is proven", 1.0)
            # custom final step formatting
            log(f"\n{title}")

            state = final_result.get("state")
            safe = "YES" if final_result.get("safe_to_act") else "NO"
            action = final_result.get("final_action")

            log(f"State: {state}")
            log(f"Safe to act: {safe}")
            log(f"Action: {action}")
            log("→ Execution allowed only after stability is proven")
        else:
            print_step(title, final_result)
            wait(1.0)

    log("")
    assert_equal("Recovery Validation final state", final_result["state"], "STABLE")
    assert_equal("Recovery Validation final action", final_result["final_action"], "proceed")
    assert_equal("Recovery Validation execution status", final_result["execution_status"], "executed")


def run_dependency_blocking():
    clear()
    header(
        "SCENARIO 02 - DEPENDENCY BLOCKING",
        "Demonstrates that a locally stable service can still be blocked when a dependency is DEGRADED."
    )
    baseline("A dependent service appears healthy and proceeds anyway.")

    reset_demo()

    steps = [
        ("service-a fails", {
            "service_name": "service-a",
            "signal_type": "failure",
            "dependencies": [],
        }),
        ("service-a recovers", {
            "service_name": "service-a",
            "signal_type": "recovered",
            "dependencies": [],
        }),
        ("service-b attempts action while depending on service-a", {
            "service_name": "service-b",
            "signal_type": "stable",
            "dependencies": ["service-a"],
        }),
    ]

    beat("→ Local state is not enough — system-wide truth determines action", 1.2)

    final_result = None
    for title, payload in steps:
        final_result = post("/evaluate", payload)

        # Normal step output
        print_step(title, final_result)
        wait(1.0)

        if payload["service_name"] == "service-b":
            beat(f"\n{BOLD}Propagation:{RESET}", 0.2)
            beat("Upstream dependency (service-a): DEGRADED", 0.15)
            system_posture = (
               final_result.get("system_posture")
               or final_result.get("coordination", {}).get("system_posture")
               or "DEGRADED"
            )
            beat(f"System posture: {color_state(system_posture)}", 0.15)
            beat(f"Safe to act (service-b): {color_safe(bool(final_result.get('safe_to_act')))}", 0.2)
            beat("→ Safe-to-act propagated across dependency boundary", 0.6)
            beat("→ Local state is not enough — system-wide truth determines action", 1.0)
    log("")
    assert_equal("Dependency Blocking final state", final_result["state"], "STABLE")
    assert_equal("Dependency Blocking final action", final_result["final_action"], "no_action")
    assert_equal("Dependency Blocking execution status", final_result["execution_status"], "suppressed")
    assert_equal("Dependency Blocking safe_to_act", final_result["safe_to_act"], False)


def run_control_transformation():
    clear()
    header(
        "SCENARIO 03 - CONTROL TRANSFORMATION VIA GATE",
        "Demonstrates that a preferred action can be transformed under degraded posture before enforcement."
    )
    baseline("A healthy-looking service proceeds at full power.")

    reset_demo()

    steps = [
        ("service-a fails", {
            "service_name": "service-a",
            "signal_type": "failure",
            "dependencies": [],
        }),
        ("service-a recovers", {
            "service_name": "service-a",
            "signal_type": "recovered",
            "dependencies": [],
        }),
        ("service-b proceeds under degraded posture", {
            "service_name": "service-b",
            "signal_type": "stable",
            "dependencies": [],
        }),
    ]

    beat("→ Actions can be reduced, not just allowed or blocked", 1.0)

    final_result = None
    for title, payload in steps:
        final_result = post("/evaluate", payload)
        print_step(title, final_result)
        wait(1.0)

def run_policy_toggle_effect():
    clear()
    header(
    "SCENARIO 04 - POLICY TOGGLE EFFECT",
    "Demonstrates that runtime policy toggling changes the final enforced action for the same preferred action."
    )
    baseline("The same action always executes the same way unless the system itself changes.")

    # ---- Phase A: policy enabled ----
    reset_demo()

    enabled_steps = [
        ("service-a fails", {
            "service_name": "service-a",
            "signal_type": "failure",
            "dependencies": [],
        }),
        ("service-a recovers", {
            "service_name": "service-a",
            "signal_type": "recovered",
            "dependencies": [],
        }),
        ("service-b proceeds under degraded posture (policy enabled)", {
            "service_name": "service-b",
            "signal_type": "stable",
            "dependencies": [],
        }),
    ]

    enabled_result = None
    for title, payload in enabled_steps:
        enabled_result = post("/evaluate", payload)
        print_step(title, enabled_result)
        wait(1.0)

    log("")
    assert_equal("Policy Toggle enabled preferred action", enabled_result["preferred_action"], "proceed")
    assert_equal("Policy Toggle enabled final action", enabled_result["final_action"], "limited_action")
    assert_equal("Policy Toggle enabled execution status", enabled_result["execution_status"], "restricted_execution")
    assert_equal("Policy Toggle enabled policy name", enabled_result["policy_name"], "degraded_posture")

    # ---- Phase B: policy disabled ----
    reset_demo()
    set_policy("degraded_posture", False)

    disabled_steps = [
        ("service-a fails", {
            "service_name": "service-a",
            "signal_type": "failure",
            "dependencies": [],
        }),
        ("service-a recovers", {
            "service_name": "service-a",
            "signal_type": "recovered",
            "dependencies": [],
        }),
        ("service-b proceeds under degraded posture (policy disabled)", {
            "service_name": "service-b",
            "signal_type": "stable",
            "dependencies": [],
        }),
    ]

    disabled_result = None
    for title, payload in disabled_steps:
        disabled_result = post("/evaluate", payload)
        print_step(title, disabled_result)
        wait(1.0)

    log("")
    assert_equal("Policy Toggle disabled preferred action", disabled_result["preferred_action"], "proceed")
    assert_equal("Policy Toggle disabled final action", disabled_result["final_action"], "proceed")
    assert_equal("Policy Toggle disabled execution status", disabled_result["execution_status"], "executed")
    assert_equal("Policy Toggle disabled policy name", disabled_result["policy_name"], None)

    # Optional cleanup: restore policy for future runs
    set_policy("degraded_posture", True)

def run_cross_system_governance():
    clear()
    header(
        "SCENARIO 05 - CROSS-SYSTEM GOVERNANCE",
        "Demonstrates that execution requests from an external or separate system are governed before execution based on system-wide conditions."
    )
    baseline("An external request is executed as long as the target service appears ready.")

    reset_demo()

    steps = [
        ("service-a fails", {
            "service_name": "service-a",
            "signal_type": "failure",
            "dependencies": [],
        }),
        ("service-a recovers", {
            "service_name": "service-a",
            "signal_type": "recovered",
            "dependencies": [],
        }),
        ("external-system requests service-b execution while system remains degraded", {
            "service_name": "service-b",
            "signal_type": "stable",
            "dependencies": [],
            "request_source": "external_system",
        }),
    ]

    beat("→ External requests are governed before execution", 1.0)

    final_result = None
    for title, payload in steps:
        final_result = post("/evaluate", payload)
        print_step(title, final_result)
        wait(1.0)

    if payload.get("request_source") == "external_system":
        beat("→ External requests are governed before execution", 0.9)

    log("")
    assert_equal("Cross-System Governance final state", final_result["state"], "STABLE")
    assert_equal("Cross-System Governance preferred action", final_result["preferred_action"], "proceed")
    assert_equal("Cross-System Governance final action", final_result["final_action"], "limited_action")
    assert_equal("Cross-System Governance execution status", final_result["execution_status"], "restricted_execution")
    assert_equal("Cross-System Governance governance decision", final_result["governance_decision"], "modify")

def run_safe_to_act_propagation():
    clear()
    header(
        "SCENARIO 06 - SAFE-TO-ACT PROPAGATION",
        "Demonstrates that instability in one part of the system propagates execution restrictions across multiple services."
    )
    baseline("One service fails, but other services continue acting independently.")

    reset_demo()

    steps = [
        ("service-a fails", {
            "service_name": "service-a",
            "signal_type": "failure",
            "dependencies": [],
        }),
        ("service-b attempts to act", {
            "service_name": "service-b",
            "signal_type": "stable",
            "dependencies": [],
        }),
        ("service-c attempts to act", {
            "service_name": "service-c",
            "signal_type": "stable",
            "dependencies": [],
        }),
    ]

    beat("→ One service failure changed what the rest of the system was allowed to do", 1.2)

    results = []

    for title, payload in steps:
        result = post("/evaluate", payload)
        results.append((title, result))
        print_step(title, result)
        wait(1.0)

        if payload["service_name"] in ["service-b", "service-c"]:
            beat(f"\n{BOLD}Propagation:{RESET}", 0.2)
            beat("Originating instability: service-a = UNSTABLE", 0.15)
            system_posture = (
                result.get("system_posture")
                or result.get("coordination", {}).get("system_posture")
                or "UNSTABLE"
            )
            beat(f"System posture: {color_state(system_posture)}", 0.15)
            beat(f"Safe to act ({payload['service_name']}): {color_safe(bool(result.get('safe_to_act')))}", 0.2)
            beat("→ Safe-to-act restriction propagated across the system", 0.6)
            beat("→ One service failure changed what the rest of the system was allowed to do", 1.0)
    # Final checks use service-b and service-c
    service_b_result = results[1][1]
    service_c_result = results[2][1]

    log("")
    assert_equal("Safe-to-Act Propagation service-b safe_to_act", service_b_result["safe_to_act"], False)
    assert_equal("Safe-to-Act Propagation service-c safe_to_act", service_c_result["safe_to_act"], False)
    assert_equal("Safe-to-Act Propagation service-b final action", service_b_result["final_action"], "no_action")
    assert_equal("Safe-to-Act Propagation service-c final action", service_c_result["final_action"], "no_action")

def main():
    # ---- INTRO ----
    clear()

    beat("Most systems monitor events and react locally.", 1.2)
    beat("This system determines whether software is allowed to act before it executes.", 1.6)

    wait(1.0)

    health = get("/health")
    if SHOW_INTERNALS:
        log(f"[health] {health}")

    # ---- SCENARIOS ----
    run_recovery_validation()
    run_dependency_blocking()
    run_control_transformation()
    run_policy_toggle_effect()
    run_cross_system_governance()
    run_safe_to_act_propagation()

    # ---- FINAL TAKEAWAY ----
    wait(1.0)
    clear()

    beat(f"\n{DIM}=============================={RESET}", 0.2)
    beat(f"{BOLD}FINAL TAKEAWAY{RESET}", 0.3)
    beat(f"{DIM}=============================={RESET}", 0.6)

    wait(0.5)

    beat("Systems shouldn't act on incomplete truth.", 1.2, delay=0.012)
    beat("Sentra determines whether systems are allowed to act at all.", 1.8, delay=0.012)

    wait(2.0)

    # ---- CLOSING ----
    clear()

    beat("Sentra", 1.0, delay=0.012)
    beat("Execution, governed.", 2.0, delay=0.012)

    wait(2.0)

    save_output("demo_output.txt")
    if SHOW_INTERNALS:
        beat(f"\n{DIM}[done] Demo output saved to demo_output.txt{RESET}", 0.4)

if __name__ == "__main__":
    main()
