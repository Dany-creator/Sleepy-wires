import anthropic
import json

def compare_designs (reference_profile, candidate_profile, anthropic_key):
    """Claude integrated"""
    
    client = anthropic.Anthropic(api_key=anthropic_key)

    system_prompt = """You are a design comparison assistant.
    
    You DO NOT judge designs in isolation.
    You ONLY compare a candidate design to a reference design profile.
    You must cite specific numeric differences

    Output ONLY valid JSON in this format:
    {
        "deviations":[
            {
        "area": "specific metric name",
        "reference_value": "exact value from reference",
        "candidate_value": "exact value from candidate",
        "impact": "brief explanation of user impact",
        "severity": "low|medium|high
            }
        ]
        "overall_assessment": "one sentence summary"
    }
    If profiles are too different to compare meaningfully, include "comparison_confidence": "low"
    """

    user_message = f"""Compare these two design profiles:

    REFERENCE (proven design):
    {json.dumps(reference_profile, indent=2)}

    CANDIDATE (design to evaluate):
    {json.dumps(candidate_profile, indent=2)}
    

    Identify meaningful deviations that could impact user experience"""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}]
    )
    
    # Claude's response
    response_text = message.content[0].text

    #jsom
    if "```json" in response_text:
        response_text = response_text.split("```json")[1].split("```")[0]
    elif "```" in response_text:
        response_text = response_text.split("```")[1].split("```")[0]

    comparison = json.loads(response_text.strip())
    return comparison