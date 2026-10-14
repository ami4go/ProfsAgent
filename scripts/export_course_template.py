"""Fill the official IIIT-D CSE course description template (xlsx) from a design run.

  python scripts/export_course_template.py --run-id cs601-01

Writes runs/<run-id>/course_template.xlsx (also produced automatically when a run renders its proposal).
Source template: templates/iiitd_cse_course_template.xlsx. No LLM.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from profsagent.render.course_template import write_xlsx  # noqa: E402

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-id", required=True)
    run = ROOT / "runs" / ap.parse_args().run_id
    st = json.loads((run / "state.json").read_text(encoding="utf-8"))
    print(write_xlsx(st, run / "course_template.xlsx"))
