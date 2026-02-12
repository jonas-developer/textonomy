import os, json, math
from typing import List

from api.schemas import ModelJudgement, UnifiedResult

from langchain_openai import ChatOpenAI
from langchain_deepseek import ChatDeepSeek
from langchain_ibm import ChatWatsonx


def _max_tokens() -> int:
    # In the .env: MAX_GENERATIONS=1000
    try:
        return int(os.getenv("MAX_GENERATIONS", "1000"))
    except ValueError:
        return 1000


RUBRIC = """
Score how strongly this text matches LLM-generated writing patterns vs human writing.

Return ai_likelihood_score 0..100:
0-20 very likely human
21-49 probably human / mixed
50-69 unclear
70-89 probably AI-assisted
90-100 very likely AI-written

Use multiple signals:
- Em Dashes: em dashes used is a strong 70% signal
- Uniformity: oddly consistent sentence length, tone, formatting
- Genericness: high-level claims, low concrete detail
- Template transitions: “Additionally”, “Furthermore”, “In conclusion”
- Over-hedging: “generally”, “typically”, “important to note”
- Repetition / paraphrase loops
- Lack of human artifacts: messy edits, quirks, genuine uncertainty
- Over-coverage: smooth comprehensive answer without natural gaps

Hard rules:
- Do NOT claim certainty.
- Provide 3–7 signals.
- Provide 0–4 short evidence snippets (<=20 words each).
- Reasoning <=120 words.
- Output ONLY valid JSON:
{"ai_likelihood_score": 0-100, "reasoning": "...", "signals": [...], "evidence": [...]}
""".strip()


def _provider_focus(provider: str) -> str:
    return {
        "openai": "Extra focus: overly polished structure and safe hedging.",
        "deepseek": "Extra focus: repetition, paraphrase loops, uniform rhythm.",
        "watsonx": "Extra focus: genericness vs concrete specifics and internal consistency.",
    }.get(provider, "")


def _prompt(provider: str, text: str) -> str:
    return f"{RUBRIC}\n\nProvider focus: {_provider_focus(provider)}\n\nTEXT:\n{text}"


def _parse_json_only(s: str) -> dict:
    a = s.find("{")
    b = s.rfind("}")
    if a == -1 or b == -1 or b <= a:
        raise ValueError(f"Model returned non-JSON output: {s[:200]}")
    return json.loads(s[a : b + 1])


def _judge(chat, provider: str, model_name: str, text: str) -> ModelJudgement:
    raw = chat.invoke(_prompt(provider, text))
    content = getattr(raw, "content", str(raw))
    data = _parse_json_only(content)
    return ModelJudgement(
        provider=provider,
        model=model_name,
        ai_likelihood_score=int(data["ai_likelihood_score"]),
        reasoning=str(data["reasoning"]),
        signals=list(data.get("signals", [])),
        evidence=list(data.get("evidence", [])),
    )


def _watsonx_client(max_out: int) -> tuple[ChatWatsonx, str]:
    """
    Best practice: set watsonx creds as JSON in WATSONX_CREDENTIALS, e.g.
    {"apikey":"...","url":"...","project_id":"..."} (or space_id).
    If your WATSONX_CREDENTIALS is not JSON, you'll likely need to add
    separate env vars (WATSONX_API_KEY / etc.) matching your IBM setup.
    """
    model_id = os.getenv("WATSONX_MODEL", "mistralai/mistral-small-3-1-24b-instruct-2503")
    creds_raw = (os.getenv("WATSONX_CREDENTIALS") or "").strip()

    kwargs = {
        "model_id": model_id,
        "temperature": 0,
        "max_new_tokens": max_out,
    }

    if creds_raw:
        try:
            creds = json.loads(creds_raw)
            # Common watsonx fields
            if "apikey" in creds:
                kwargs["api_key"] = creds["apikey"]
            if "url" in creds:
                kwargs["url"] = creds["url"]
            if "project_id" in creds:
                kwargs["project_id"] = creds["project_id"]
            if "space_id" in creds:
                kwargs["space_id"] = creds["space_id"]
        except Exception:
            # Not JSON -> leave kwargs as-is; you'll need proper env vars.
            pass

    return ChatWatsonx(**kwargs), model_id


def run_panel(text: str) -> UnifiedResult:
    max_out = _max_tokens()

    openai_model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
    deepseek_model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

    openai = ChatOpenAI(model=openai_model, temperature=0, max_tokens=max_out, timeout=60)
    deepseek = ChatDeepSeek(model=deepseek_model, temperature=0, max_tokens=max_out, timeout=60)
    watsonx, watsonx_model_id = _watsonx_client(max_out)

    per_model: List[ModelJudgement] = [
        _judge(openai, "openai", openai_model, text),
        _judge(deepseek, "deepseek", deepseek_model, text),
        _judge(watsonx, "watsonx", watsonx_model_id, text),
    ]

    scores = [m.ai_likelihood_score for m in per_model]
    mean = sum(scores) / len(scores)
    stdev = math.sqrt(sum((s - mean) ** 2 for s in scores) / len(scores))

    final_score = int(round(mean))
    confidence = "high" if stdev <= 8 else "medium" if stdev <= 18 else "low"

    final_label = "RED" if final_score >= 70 else "YELLOW" if final_score >= 40 else "GREEN"
    notes = f"mean={mean:.1f}, stdev={stdev:.1f} (agreement -> confidence)"

    return UnifiedResult(
        final_label=final_label,
        final_score=final_score,
        confidence=confidence,
        aggregation_notes=notes,
        per_model=per_model,
    )
