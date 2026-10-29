"""Step 4-5 of the flow: run the extraction prompt on proposal text files, then validate.

Usage:
  python3 extract.py proposals_dir/            # needs ANTHROPIC_API_KEY in the environment
  python3 extract.py proposals_dir/ --dry-run  # prints the prompt only, no API call

Each proposal is a .txt file (text already extracted from the PDF). The file name
(e.g. A.txt) becomes the proposal id. Output: out/extractions.json, in the format
score.py reads. Fields that fail validation are set to None, which score.py flags.
"""
import json, os, re, sys, pathlib

HERE = pathlib.Path(__file__).resolve().parent
MODEL = os.environ.get("EXTRACT_MODEL", "claude-sonnet-5-5")

def load_system_prompt():
    md = (HERE.parent / "PROMPTS.md").read_text()
    section = md.split("### System message", 1)[1].split("### User message", 1)[0]
    return re.search(r"```\n(.*?)\n```", section, re.S).group(1)

def user_message(text):
    return ("Category: Commercial Solar Installation\nCriteria version: solar-commercial-v1\n"
            "Extract the facts for this category from the proposal below.\n\n"
            f"<proposal>\n{text}\n</proposal>")

def norm(s):
    return re.sub(r"\s+", " ", s).strip().lower()

def quote_ok(field, source):
    """A value is accepted only if its evidence quote appears verbatim in the source."""
    if not isinstance(field, dict) or field.get("value") is None:
        return True
    ev = field.get("evidence")
    return bool(ev and ev.get("quote") and norm(ev["quote"]) in norm(source))

def to_flat(raw, source):
    def val(name):
        f = raw.get(name)
        return f["value"] if f and quote_ok(f, source) else None
    inj = bool(raw.get("injection_detected")) or raw.get("extraction_confidence") == "low"
    return {
        "licence_held": val("licence_held_by_bidder"),
        "wsib_confirmed": val("wsib_clearance_confirmed"),
        "insurance_5m_confirmed": val("liability_insurance_5m_confirmed"),
        "injection_flag": inj,
        "qualifying_installs": val("qualifying_installs") or 0,
        "price": val("total_price_cad"),
        "weeks": val("completion_weeks"),
        "panel_years": val("panel_warranty_years") or 0,
        "workmanship_years": val("workmanship_warranty_years") or 0,
        "lead_named": bool(val("named_project_lead")),
        "crew_stated": bool(val("crew_size_stated")),
        "safety_plan": bool(val("safety_plan")),
        "monitoring_plan": bool(val("monitoring_plan")),
    }

def call_model(system, user):
    import anthropic  # pip install anthropic
    client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY
    msg = client.messages.create(model=MODEL, max_tokens=2000, temperature=0,
                                 system=system, messages=[{"role": "user", "content": user}])
    return json.loads(msg.content[0].text)

def main(folder, dry):
    system = load_system_prompt().replace("{{five_years_ago_year}}", "2021")
    files = sorted(pathlib.Path(folder).glob("*.txt"))
    out, raws = {}, {}
    for f in files:
        text = f.read_text()
        if dry:
            print(f"--- {f.stem} ---\n{user_message(text)[:300]}...\n")
            continue
        raw = call_model(system, user_message(text))
        raws[f.stem], out[f.stem] = raw, to_flat(raw, text)
    if not dry:
        pathlib.Path("out").mkdir(exist_ok=True)
        json.dump(out, open("out/extractions.json", "w"), indent=1)
        json.dump(raws, open("out/raw_ai_output.json", "w"), indent=1)  # kept for the audit log
        print("wrote out/extractions.json  ->  python3 score.py out/extractions.json criteria.json")

if __name__ == "__main__":
    main(sys.argv[1], "--dry-run" in sys.argv)
