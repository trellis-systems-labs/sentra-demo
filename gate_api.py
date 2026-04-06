from flask import Flask, request, jsonify

from transition_engine import TransitionEngine
from signals import Signal
from state_model import STABLE

app = Flask(__name__)

engine = TransitionEngine(window_size=4, confidence_threshold=4.0)

service_states = {
    "service-a": STABLE,
    "service-b": STABLE,
}


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


@app.route("/policies", methods=["GET"])
def policies():
    return jsonify({"policies": engine.list_policies()}), 200

@app.route("/reset", methods=["POST"])
def reset():
    global engine
    engine = TransitionEngine()
    return jsonify({"status": "reset"}), 200

@app.route("/policy", methods=["POST"])
def set_policy():
    data = request.get_json(force=True)

    policy_name = data.get("policy_name")
    enabled = data.get("enabled")

    if policy_name is None or enabled is None:
        return jsonify({"error": "policy_name and enabled are required"}), 400

    updated = engine.set_policy_enabled(policy_name, bool(enabled))

    if not updated:
        return jsonify({"error": f"policy '{policy_name}' not found"}), 404

    return jsonify({
        "status": "updated",
        "policy_name": policy_name,
        "enabled": bool(enabled),
        "policies": engine.list_policies(),
    }), 200

@app.route("/evaluate", methods=["POST"])
def evaluate():
    data = request.get_json(force=True)

    service_name = data.get("service_name", "unknown-service")
    signal_type = data.get("signal_type", "stable")
    dependencies = data.get("dependencies", [])

    result = engine.evaluate(
        service_name=service_name,
        signal_type=signal_type,
        dependencies=dependencies,
    )

    request_source = data.get("request_source", "internal")

    response = {
        "service_name": service_name,
        "signal_type": result["signal"]["signal_type"],
        "state": result["state"],
        "safe_to_act": result["safe_to_act"],
        "preferred_action": result["decision"]["preferred_action"],
        "final_action": result["control"]["final_action"],
        "execution_status": result["enforcement"]["execution_status"],
        "system_posture": result["coordination"]["system_posture"],
        "service_states": result["coordination"]["service_states"],
        "coordination_reason": result["coordination_reason"],
        "transformation_reason": result["control"]["transformation_reason"],
        "policy_name": result["control"]["policy_name"],
        "policy_priority": result["control"]["policy_priority"],
        "governance_decision": result["governance_decision"],
        "request_source": request_source,
        "enforcement_reason": result["enforcement"]["enforcement_reason"],
        "active_policies": result["control"]["active_policies"],
    }

    return jsonify(response)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9007, debug=False)
