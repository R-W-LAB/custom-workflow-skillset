# Choice-Assisted Question Contract

Use for `deep-interview`, `design-grill`, and `design-grill-with-docs` whenever options help the user make one clear decision.

## Plan mode adapter

When `request_user_input` is available:
- Ask exactly one question per call.
- Provide 2-3 mutually exclusive options.
- Put the recommended option first and suffix its label with `(Recommended)`.
- Keep labels to 1-5 words and descriptions to one short sentence about impact or tradeoff.
- Do not include an `Other` option manually; the Plan mode client adds free-form Other.
- Normalize the selected or free-form answer into the Decision Log.

## Markdown fallback

When `request_user_input` is unavailable:

```md
Question <n>: <one clear decision question>

Recommended options:
A. <option> - <short tradeoff>
B. <option> - <short tradeoff>
C. <option> - <short tradeoff, optional>
D. Other / custom answer - describe what you want instead.

My default recommendation: <A/B/C> because <one-line reason>.
```

Prefer 2 options for simple decisions, 3 only for genuinely distinct paths. Use open-ended questions when options would bias the user or hide an important unknown.
