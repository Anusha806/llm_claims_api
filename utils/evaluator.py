def evaluate(parsed_query: dict, matched_clause: str) -> dict:
    procedure = parsed_query.get("procedure", "")
    duration = parsed_query.get("policy_duration", "")

    if not matched_clause or not procedure:
        return {
            "decision": "rejected",
            "justification": "Unable to match clause or detect procedure from query.",
            "amount": "₹0"
        }

    if procedure.lower() in matched_clause.lower():
        return {
            "decision": "approved",
            "justification": f"{procedure.capitalize()} is covered under the policy. Clause matched.",
            "amount": "₹80,000"
        }

    return {
        "decision": "rejected",
        "justification": "Procedure not clearly mentioned in policy document.",
        "amount": "₹0"
    }
