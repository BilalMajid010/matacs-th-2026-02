# Prototype

Two small scripts that follow the flow in `diagram/process-flow.png`.

| Script | Flow step | Uses AI? |
|---|---|---|
| `extract.py` | 4 extraction and 5 validation | Yes (one call per proposal) |
| `score.py` | 6 mandatory gate, 7 scoring, 9 ranking | No |

## Run

```
cp ../.env.example ../.env          # add your API key to .env, and export it
pip install anthropic
python3 extract.py my_proposals/    # folder of A.txt, B.txt ... (text taken from the PDFs)
python3 score.py out/extractions.json criteria.json
```

`extract.py` reads the system prompt straight from `../PROMPTS.md`, so the prompt that is documented is the prompt that runs. Add `--dry-run` to print the messages without calling the API. Proposal text is not stored in this repository.

## No API key?

`extractions.json` holds the facts I extracted by hand for A to E, so this works without a key:

```
python3 score.py extractions.json criteria.json
```

It prints the same ranking as `../ranking.json`. Running it twice gives identical output, and changing a weight in `criteria.json` re-scores with no AI call.

## What is validated

- A value is kept only if its evidence quote appears word for word in the proposal text. Otherwise it becomes `null`, and `score.py` flags the proposal for a human.
- `injection_flag` is set when the model reports text aimed at the review system, or when its confidence is low. Flagged proposals are never ranked automatically.
