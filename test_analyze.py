import json
import sys
from typing import Any, Dict

import requests


API_URL = "http://127.0.0.1:8000/api/analyze/"
DEFAULT_TEXT = (
    "It is with due diligence and reference to the prevailing standards of professional conduct that I address the matter at hand. My analysis of the contractual provisions, specifically Clause 14.2, reveals a material ambiguity with respect to performance timelines and consequential remedies. I must advise that reliance upon the opposing party’s informal representations, absent written amendment duly executed, constitutes substantial legal risk. Furthermore, the omission of a force majeure provision renders the agreement vulnerable to unforeseen supervening events. It is therefore my considered opinion that renegotiation is not merely prudent but necessary. Should litigation ensue, the current drafting invites adverse judicial construction. Your immediate instruction is respectfully requested."
)

def print_section(title: str) -> None:
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)

def main() -> None:
    text = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_TEXT

    payload = {"text": text}
    resp = requests.post(API_URL, json=payload, timeout=120)

    print_section(f"HTTP {resp.status_code}")
    try:
        data: Dict[str, Any] = resp.json()
    except Exception:
        print(resp.text)
        return

    if resp.status_code != 200:
        print(json.dumps(data, indent=2, ensure_ascii=False))
        return

    # Structured summary
    print_section("Unified Result")
    print(f"Label      : {data.get('final_label')}")
    print(f"Score      : {data.get('final_score')}")
    print(f"Confidence : {data.get('confidence')}")
    print(f"Notes      : {data.get('aggregation_notes')}")

    print_section("Per-Model Judgements")
    for j in data.get("per_model", []):
        print(f"- Provider: {j.get('provider')} | Model: {j.get('model')} | Score: {j.get('ai_likelihood_score')}")
        print(f"  Reasoning: {j.get('reasoning')}")
        signals = j.get("signals") or []
        evidence = j.get("evidence") or []
        if signals:
            print("  Signals:")
            for s in signals:
                print(f"    • {s}")
        if evidence:
            print("  Evidence:")
            for e in evidence:
                print(f"    “{e}”")
        print()

    print_section("Raw JSON")
    print(json.dumps(data, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
