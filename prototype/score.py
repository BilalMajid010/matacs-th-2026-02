"""Deterministic scoring + ranking. Input: validated extraction JSON (output of the AI
extraction step) and the admin's criteria snapshot. No AI is used here: same input,
same output. Usage: python score.py extractions.json criteria.json > ranking.json"""
import json, sys

def gate(p):
    """Mandatory pass/fail checks. Returns (status, notes)."""
    musts = [p["licence_held"], p["wsib_confirmed"], p["insurance_5m_confirmed"]]
    if any(m is False for m in musts):
        return "ineligible", "failed a mandatory criterion"
    if any(m is None for m in musts):
        return "flagged", "mandatory criterion unclear"
    if p["injection_flag"]:
        return "flagged", "embedded instruction aimed at the review system"
    if p["weeks"] is None:
        return "flagged", "no completion time stated"
    if p["price"] > CR["budget_ceiling"] or p["weeks"] > CR["max_weeks"]:
        return "flagged", "outside budget ceiling or 16-week limit"
    return "ranked", ""

def main(ext_path, cr_path):
    global CR
    ext, CR = json.load(open(ext_path)), json.load(open(cr_path))
    w = CR["weights"]
    status = {k: gate(v) for k, v in ext.items()}
    pool = [k for k in ext if status[k][0] != "ineligible"]
    low_price = min(ext[k]["price"] for k in pool)
    weeks = [ext[k]["weeks"] for k in pool if ext[k]["weeks"]]
    low_weeks = min(weeks)
    out = {}
    for k in pool:
        p = ext[k]
        s = {
          "experience": min(p["qualifying_installs"], CR["experience_full_marks_at"]) / CR["experience_full_marks_at"],
          "price": low_price / p["price"],
          "timeline": (low_weeks / p["weeks"]) if p["weeks"] else 0.0,
          "warranty": 0.5 * min(p["panel_years"] / CR["warranty_full_marks"]["panel_years"], 1)
                    + 0.5 * min(p["workmanship_years"] / CR["warranty_full_marks"]["workmanship_years"], 1),
          "team": sum([p["lead_named"], p["crew_stated"], p["safety_plan"], p["monitoring_plan"]]) / 4,
        }
        out[k] = (round(sum(s[c] * w[c] for c in w), 1), s)
    ranked = sorted([k for k in pool if status[k][0] == "ranked"],
                    key=lambda k: (-out[k][0], ext[k]["price"], k))
    result = []
    for k in sorted(ext):
        st, note = status[k]
        rank = ranked.index(k) + 1 if k in ranked else None
        score = out[k][0] if k in out else None
        result.append({"proposal": k, "rank": rank, "status": st, "score": score,
                       "detail": {c: round(v * 100, 1) for c, v in out[k][1].items()} if k in out else None,
                       "note": note})
    print(json.dumps(result, indent=1))

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
