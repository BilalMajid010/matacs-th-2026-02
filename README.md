# MATACS-TH-2026-02: AI Proposal Triage Design

**Full name:** Syed Bilal Majid
**Reference:** MATACS-TH-2026-02
**Time actually spent:** About 1 hour 30 minutes (roughly 60 minutes designing and drafting with AI help, then about 30 minutes reviewing it against the brief and correcting it).

## Summary

A design for an AI-assisted proposal triage tool. AI reads each proposal and extracts facts with word-for-word evidence. Plain code checks that evidence, applies the mandatory pass/fail rules, scores and ranks. A person reviews the result and makes the award. Proposals are referred to by letter (A to E). Result: A is ranked 1, E is ranked 2, C and D are flagged for a human, and B is ineligible.

## Files

- [WRITEUP.md](WRITEUP.md): answers to the five questions
- [diagram/process-flow.png](diagram/process-flow.png): flow from upload to ranked output, showing AI steps, rule steps and human checkpoints
- [PROMPTS.md](PROMPTS.md): the extraction and qualitative-scoring prompts
- [ranking.json](ranking.json): expected ranking of proposals A to E
- [prototype/](prototype/): optional scripts that run the extraction prompt and score the result ([prototype/README.md](prototype/README.md))
- [.env.example](.env.example): the only place an API key is mentioned; no real key is committed

## How I used AI tools

I used Claude to draft the flow, the prompts, the write-up and the scoring script, and then reviewed everything against the brief myself. I corrected it in three places. The first draft of the write-up was 1,123 words, over the 1,000 limit, so I had it cut to under 940. The first prototype only scored hand-typed data and never ran a prompt, so I added `extract.py`, which runs the real prompt and rejects any value whose quote is not in the proposal. I also disagreed with an early idea of giving a proposal with no stated timeline a score of zero, because that hides a gap from the reviewer. It is now flagged and the bidder is asked.
