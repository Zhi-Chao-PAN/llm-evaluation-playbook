# 03 · Contamination Control: Reference-Answer Isolation

The single most expensive evaluation bug: the reference answer, the rubric, or a scoring hint ends up visible to the model under test. After that, every score measures recall, not capability — and the contamination is usually silent.

## The two namespaces

Design every task as two disjoint namespaces:

```text
AGENT namespace (what the model sees)
├── user prompt
├── task attachments (the "documents a real user would have")
└── prior-turn user messages

JUDGE namespace (reviewer/tooling only)
├── reference answer
├── rubric + tolerance specs
├── canonical prior outputs
└── scoring notes / known failure modes
```

The rule is one sentence: **the agent namespace must be reconstructable as a plausible real-world request.** If a real user would never paste the reference answer into their prompt, it must not be there.

## Attachment visibility matrix

For multi-file tasks, write the matrix explicitly and check it before packaging:

| Asset | Agent | Judge | Notes |
|---|---|---|---|
| Input dataset (CSV) | ✔ | ✔ | the "real" data |
| Glossary of domain terms | ✔ | ✔ | fair game |
| Reference answer | ✘ | ✔ | judge only, always |
| Rubric | ✘ | ✔ | judge only, always |
| Tolerance specs (JSON) | ✘ | ✔ | judge/tooling only |
| Prior-turn canonical outputs | ✘ (frozen versions go in agent turns) | ✔ | see 04 |

Common leak paths, in rough order of frequency:

1. **File naming** — `reference_answer_v2.csv` inside the agent bundle. Name judge assets with a `_judge` prefix and exclude by pattern at packaging time.
2. **Prompt assembly scripts** — a template variable that interpolates the gold answer "for context". Delete the variable, not just its default.
3. **Chat history copy-paste** — discussing scoring with a colleague *in the same thread* the model can see. Keep judge discussion in a separate channel/doc.
4. **Zip packaging** — the bundle shipped to annotators accidentally contains the judge folder. Unzip and list every file before sending; check, don't trust the build script.
5. **Metadata** — document titles, sheet names, cell comments carrying hints ("this is where most models fail").

## Isolation hygiene checklist

- [ ] Every judge asset name matches `*_judge*` and packaging excludes that pattern
- [ ] The agent bundle has been unzipped on a clean machine and every file read top-to-bottom
- [ ] No tolerance spec, rubric fragment, or gold number appears anywhere in the agent namespace (grep for the gold values themselves)
- [ ] Prior-turn messages given to the model are the **frozen canonical versions**, not live outputs
- [ ] A second person (or a script) re-derives the agent namespace from the task spec alone and confirms nothing extra arrived

The grep trick in item 3 is cheap and catches real leaks: take the top-3 numeric gold values, search the entire agent bundle for their string forms (and 1–2 plausible roundings). Gold numbers have fingerprints.
