"""Which LLM endpoints in config/models.yaml answer right now? One tiny JSON call per (provider, model), first key only.

    python scripts/check_llm.py                 # every role
    python scripts/check_llm.py --provider nvidia,mistral

Prints ok / the error per endpoint and which providers have no keys in .env. Uses a few requests of each free quota;
Gemini is skipped unless named with --provider, since its free daily quota is the scarcest.
"""
from __future__ import annotations

import argparse
import sys
import time

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[1] / "src"))

from profsagent.llm.client import LLMClient, _HTTPError  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--provider", help="comma-separated providers to check (default: all except gemini)")
    args = ap.parse_args()
    want = set(args.provider.split(",")) if args.provider else None
    llm = LLMClient()
    keyed = {"gemini": llm.gemini_keys, "groq": llm.groq_keys, "ollama": ["local"]} | {n: p["keys"] for n, p in llm.extra.items()}
    for n, ks in keyed.items():
        if not ks and n != "ollama":
            print(f"{n:11s} no keys in .env ({llm.extra.get(n, {}).get('keys_env', n.upper() + '_API_KEYS')})")
    seen = set()
    for role, eps in llm.cfg["roles"].items():
        for ep in eps:
            prov, model = ep["provider"], ep["model"]
            if (prov, model) in seen or role == "search" or prov == "ollama":
                continue
            seen.add((prov, model))
            if (want and prov not in want) or (not want and prov == "gemini") or not keyed.get(prov):
                continue
            key = keyed[prov][0]
            t0 = time.time()
            try:
                if prov == "gemini":
                    text, _, _ = llm._gemini(model, key, "", 'Reply with the JSON {"ok": true}', 0, True)
                elif prov == "groq":
                    text, _, _ = llm._groq(model, key, "", 'Reply with the JSON {"ok": true}', 0, True)
                else:
                    text, _, _ = llm._openai(prov, model, key, "", 'Reply with the JSON {"ok": true}', 0, True)
                print(f"{prov:11s} {model:45s} ok   {time.time() - t0:5.1f}s  {text.strip()[:40]!r}")
            except _HTTPError as e:
                print(f"{prov:11s} {model:45s} FAIL HTTP {e.status}: {e.text[:120]}")
            except Exception as e:  # noqa: BLE001
                print(f"{prov:11s} {model:45s} FAIL {type(e).__name__}: {str(e)[:120]}")


if __name__ == "__main__":
    main()
