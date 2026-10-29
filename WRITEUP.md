# Write-up: AI Proposal Triage Design (MATACS-TH-2026-02)

Diagram: `diagram/process-flow.png`. Prompts: `PROMPTS.md`. Ranking: `ranking.json`.

**Design in one line:** AI reads documents; plain code makes decisions. AI turns each proposal into facts with quoted evidence. Code validates them, applies pass/fail rules, scores and ranks. A person reviews and awards.

## 1. AI vs. rules

**AI (two steps):**
- **Extraction (step 4):** proposals are free text in varied layouts, which language models handle well.
- **Qualitative judgement (step 8, optional):** only the soft part of "Team and approach", against a fixed rubric.

**Plain code:** file checks and OCR, loading criteria, validating AI output, mandatory gates, formulas, weighting, ranking, tie-breaks, reason text and the audit log.

**Where I drew the line:** anything with a right answer given the facts (arithmetic, thresholds, pass/fail) is code: exact, free and repeatable. AI only reads and interprets. It never decides who passes, does maths or picks a rank.

## 2. Consistency and explainability

- Extraction runs at temperature 0 with a strict JSON schema and pinned model and prompt versions.
- Every value carries a **verbatim quote and page**. Code checks the quote exists in the source; if not, the value is rejected, retried once, then flagged. Prices and weeks are re-parsed in code.
- Scoring is code, so the same facts always give the same scores.
- **Ranked twice, same result?** Scoring and ranking: yes. Extraction: nearly always, not guaranteed. So the validated extraction is saved and reused for re-ranks. A fresh extraction that differs is highlighted, not silently swapped in.
- **Why it ranked there:** the reviewer sees a per-criterion score table, each fact beside its quote and page, and a reason built by code from stored values, so nothing can be invented.

## 3. Human in the loop

- **Admin** sets the criteria beforehand.
- **Reviewer** sees ranked, flagged and ineligible proposals together. Flagged items are never auto-dropped; they need a human decision.
- **Overrides:** correct an extracted value, clear a flag, or move a proposal. A written reason is required.
- **Award:** a person decides. The tool has no "award" action.
- **Audit log (append-only):** file hashes, uploader, criteria version, prompt and model version, raw AI output, validated extraction, scores, flags, each override (who, when, old/new value, reason) and the final decision.

## 4. Changing criteria

- Criteria are **versioned**, and each run stores the version it used, so old results never change silently.
- After an edit, existing results are marked "scored under an older version".
- A weight change needs **no AI call**: saved extractions are re-scored in code and shown beside the old ranking. A new criterion needs extraction for that field only.
- Weights must total 100% to save. Re-scoring is chosen by the reviewer, never automatic, and both versions stay in the log.

## 5. Risks and safeguards

| Risk | Safeguard |
|---|---|
| **Wrong extraction** | Quote + page per value, quote-must-exist check, numbers re-parsed, null instead of guessing, reviewer sees evidence. |
| **Made-up facts** | Schema-checked output; unsupported values rejected; reasons built by code, not written freely by AI. |
| **Prompt injection** (hidden text telling the system what to do) | Proposal text is passed as data and the prompt says to ignore instructions in it. Extraction flags such text. Scoring is code, so a successful injection still cannot set scores. Flagged bidders go to a human. |
| **Bias** | Only criteria facts are extracted (no name, size or origin). Same prompt for all. Per-criterion scores let a reviewer spot oddities; periodic spot-check against human extraction. |
| **Missing or vague info** | Never assumed. Missing mandatory data is flagged; a missing weighted fact (like timeline) is flagged and the bidder asked, not scored 0. |
| **Gaming** | Budget and 16-week ceilings; over-limit bids flagged. |
| **Cost** | One extraction call per proposal, results cached by file hash (re-scoring is free), upload size and page limits. |
| **Security** | Allowed file types only, keys in environment variables, role-based access, retention policy. |

## Sample set result

- **A: 1st (98.0).** Passes the gates; best experience, timeline and team.
- **E: 2nd (91.7).** Passes the gates; best warranty; fewer installs than A.
- **C: flagged.** Provisional 84.8 (would be 3rd), but it contains text aimed at the review system. It goes to a human and is not rewarded for the instruction.
- **D: flagged.** Lowest price but no completion time. Ask the bidder; do not guess. With a time within 16 weeks it re-enters the ranking.
- **B: ineligible.** The licence is not the bidder's own (an unnamed subcontractor is "to be confirmed"), so it fails a mandatory criterion despite the low price.

## Assumptions

- "Licence held by the bidder" means its own licence number is stated; a promise to hire a licensed subcontractor does not count.
- Experience: qualifying installs, full marks at 10 or more. Price and timeline: relative to the best eligible bid. Warranty: half panel (25 yr full), half workmanship (12 yr full). Team: four checks (named lead, crew, safety plan, monitoring). These are my choices; an admin would set them in the criteria screen.
- Relative scoring (price, timeline) uses the best bid among those that pass the mandatory gate, flagged ones included. If a flagged bid is later removed, scores are recalculated and the reviewer sees the change in the score table.
- "Team and approach" is scored in code from four yes/no checks. The optional AI rubric (step 8) only adds a quality note for the reviewer and does not change the rank unless the admin turns it on.
