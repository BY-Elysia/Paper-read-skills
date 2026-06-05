# Visual Policy

Use this file when deciding whether to include original paper figures, original result tables, or generated explanatory diagrams. Visuals are supporting material for the academic explanation, not a separate object of analysis.

## Original Figure Priority

Prefer original figures from the paper when they show:

- model architecture
- method flow
- training pipeline
- inference pipeline
- data construction process
- benchmark or evaluation setup
- system design
- algorithm flow
- qualitative examples that clarify model behavior

Preserve figure labels and legends when possible. In the final report, place each selected figure inside the corresponding original-paper section where the method, architecture, data flow, training process, inference process, or experiment is explained.

Use cropped figure assets. The crop should contain only the figure body and necessary legend/axis labels. Avoid full-page screenshots or crops that include surrounding paragraphs. If only a full-page render is available as an intermediate artifact, crop it before embedding it in the report.

## Original Table Priority

Prefer original tables from the paper when they show:

- main results
- key ablations
- parameter count, cost, latency, or memory comparisons
- dataset, benchmark, or evaluation setup summaries
- hyperparameters needed for reproduction

Use cropped table assets. The crop should contain only the table body and necessary header/legend text, not surrounding paper prose. Place the table in the experiment or implementation section where the numbers are analyzed.

Use:

```bash
scripts/extract_tables.py paper.pdf --out-dir tables --metadata tables/metadata.json
```

## Figure Metadata

Internally record:

- figure number or candidate ID
- page
- image path
- caption
- likely type
- why this figure matters
- which report section uses it

For tables, internally record table number, page, image path, caption, bbox if available, and which claim the table supports.

Do not output a standalone figure metadata table unless the user asks for one.

## Generated Diagram Fallback

Generate an explanatory diagram only when:

- the paper has no clear architecture or flow diagram
- the original figure is unreadable
- the user asks for a simplified visual explanation
- scattered method details need one consolidated diagram

If an image generation tool is available, use it. If no image generation tool is available, output a ready-to-use prompt.

Generated diagrams should be captioned in the report as:

`根据论文内容绘制的解释性示意图`

## Grounding Rules for Generated Diagrams

Every box, arrow, label, and stage must come from:

- method section
- algorithm box
- equation
- figure caption
- experiment setup
- appendix implementation details

Do not add unsupported modules, datasets, objectives, or arrows. If a relation is inferred from multiple evidence items, state the inference naturally in the surrounding prose.

## Recommended Diagram Styles

- Clean white background
- Left-to-right or top-to-bottom flow
- Technical block diagram
- Readable labels
- Minimal decoration
- Distinct colors for input, model modules, training objectives, and outputs
- No photorealistic elements
- No decorative icons unless they clarify the paper's method

## Final Report Placement

Use figures sparingly and purposefully:

- Put an architecture figure in the architecture or method section.
- Put a training or inference flow in the method framework section.
- Put experimental setup diagrams in the experiment section.
- Put original result and ablation tables in the experiment section near the claim they support.
- Put qualitative examples only when they materially clarify behavior.
- Avoid a standalone figure-by-figure explanation section unless the user specifically asks for one.
- Avoid meta-report language about why a figure is included. Captions should directly state what the figure shows in the paper.
- Do not rely on a table image alone; explain the result logic in prose.
