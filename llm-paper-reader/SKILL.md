---
name: llm-paper-reader
description: Use when reading, summarizing, explaining, reviewing, or implementing LLM and large-model papers, including architecture, training, inference, alignment, RAG, agents, multimodal, benchmark, and systems papers. Produces formal Chinese academic Markdown reports with clear logical structure, architecture and process explanations, inline terminology, formulas with calculation-level interpretations, pseudocode for key model/training/inference flows, relevant cropped original figures/tables, and generated explanatory diagrams when the paper lacks useful visuals.
---

# LLM Paper Reader

## Goal

Read LLM-field papers and produce a formal academic explanation report that another researcher or student can read directly. Avoid generic summaries and translation-like paraphrases. Explain the paper's problem setting, complete conceptual architecture, method logic, formulas, algorithms or pseudocode, experiments, limitations, and implementation implications.

The default deliverable is a polished Chinese Markdown report, usually named `report.md`, not a collection of notes. Text extraction, figure extraction, and evidence mapping are internal preparation steps.

## When Starting

1. Prefer the original source: local PDF, arXiv HTML/PDF, paper website, official code, or provided text.
2. Extract metadata: title, authors, date or venue if available, source path or URL, and paper type.
3. If the source is a PDF, run or adapt:
   - `scripts/extract_paper_text.py paper.pdf --out paper_text.md`
   - `scripts/extract_figures.py paper.pdf --out-dir figures --metadata figures/metadata.json`
   - `scripts/extract_tables.py paper.pdf --out-dir tables --metadata tables/metadata.json`
4. When using original figures or tables, prefer cropped assets that contain only the figure/table body and necessary legend. Do not use full-page screenshots in the final report unless no usable crop can be produced.
5. Build an internal evidence map before final writing. Track section, page, figure, table, equation, algorithm, and appendix anchors for grounding, but do not expose the evidence map as a final report section.
6. Load only the needed reference files:
   - Use `references/output_templates.md` for the final report structure.
   - Use `references/architecture_checklist.md` for architecture-heavy papers.
   - Use `references/formula_explanation.md` whenever the paper contains equations, losses, algorithms, or mathematical notation.
   - Use `references/terminology_guide.md` when the paper introduces named terms, modules, metrics, datasets, or objectives.
   - Use `references/experiment_checklist.md` when analyzing experiments, baselines, ablations, or metrics.
   - Use `references/visual_policy.md` when extracting original figures or generating explanatory diagrams.

## Paper Type

Classify the paper as one or more of:

- model architecture
- training method
- inference or decoding method
- alignment, RLHF, preference optimization, or safety
- RAG, agent, memory, tool use, or data construction
- multimodal LLM
- benchmark or evaluation
- systems, serving, compression, or efficiency
- analysis, interpretability, or survey

Use the classification to decide which sections need the deepest reading.

## Required Reading Workflow

1. Skim title, abstract, introduction, and conclusion to identify the problem and claimed contributions.
2. Read the method section deeply and extract modules, data flow, objectives, algorithms, and inference-time behavior.
3. Inspect figures, tables, equations, and algorithms before writing conclusions.
4. Read experiments for datasets, baselines, metrics, main results, ablations, and failure cases.
5. Check limitations and appendix implementation details when available.
6. Produce a polished Chinese Markdown report using the output template. Preserve the paper's logical progression, but do not mechanically mirror every subsection heading.

## Evidence Rules

- Use evidence anchors internally to avoid hallucination. In the final report, cite paper locations naturally only where it helps academic reading, such as `Sec. 3`, `Fig. 2`, `Table 4`, `Eq. 1`, or appendix references.
- Use short original-text quotes only when they support a claim or define a term.
- Distinguish author claims, experimental support, and your own synthesis in prose; do not turn this distinction into a mechanical evidence-index table unless the user asks.
- If the paper omits a detail, write `原文未明确说明`.
- Do not invent modules, datasets, baselines, hyperparameters, metrics, equations, or results.
- Do not present external background knowledge as if it came from the paper.
- Do not include a final bookkeeping section that lists evidence anchors unless explicitly requested.

## Architecture Requirements

Before deep-diving into details, establish the complete conceptual architecture of the paper: what problem enters the system, what objects or modules the paper operates on, how information flows, what objective or intervention changes, and what output or conclusion is produced.

If the paper has a nontrivial training loop, inference loop, routing algorithm, retrieval process, attention mask, optimizer update, or evaluation procedure, include concise pseudocode or code-like blocks that show one complete pass through the method.

For architecture or method papers, explicitly cover:

- input and output format
- backbone or base model
- newly introduced modules
- attention, routing, retrieval, memory, tool, or multimodal interfaces
- training objectives and stages
- inference-time behavior
- computational cost, latency, or hardware assumptions if stated
- structural differences from the baseline

Use `references/architecture_checklist.md` for a complete inspection list.

## Explanation Quality Requirements

- Do not translate or paraphrase paragraph by paragraph.
- Do not merely restate the paper's outline.
- First build the full architecture or conceptual map, then explain local pieces inside that map.
- For each important mechanism, explain: what it is, why it is needed, how it works, what it consumes, what it produces, and what can go wrong.
- Prefer explanatory prose over long bullet lists. Use bullets only for dense comparisons or implementation details.
- When the paper is a survey, synthesize the field architecture: object layer, method layer, intervention layer, application layer, and evaluation layer.

## Terminology Requirements

For paper-specific terms, explain them when they first appear in the paper's logical flow. Do not create a standalone terminology chapter by default.

- original term
- Chinese explanation
- paper-specific meaning
- why it matters
- first definition or key occurrence anchor

Use `references/terminology_guide.md` for the detailed standard.

## Formula Requirements

For every important formula, explain it where it appears in the method flow. Include:

- what the formula computes
- every symbol's meaning, including dimensions when available
- the calculation steps in plain language
- implementation-level details needed to reproduce the computation, such as normalization, softmax axis, masking, positive/negative samples, averaging, max/top-k selection, or logits
- why this computation is needed
- how the formula connects to the paper's architecture, loss, algorithm, or experiment
- what assumption or limitation the formula implies

Do not place formulas in a standalone formula chapter by default. Use `references/formula_explanation.md` for the detailed standard.

## Visual Requirements

Always check whether the paper contains useful figures and tables, but use visuals as reading aids inside the relevant academic sections, not as the organizing center of the report.

Priority order:

1. Use original paper figures and result tables when available.
2. Prefer architecture diagrams, method flowcharts, training pipelines, inference pipelines, data construction diagrams, system diagrams, evaluation setup diagrams, main result tables, and ablation tables.
3. Embed selected figures/tables near the section where they clarify the architecture, method, process, or experiment.
4. If no clear original diagram exists, create a grounded explanatory diagram when an image generation tool is available.
5. If no image generation tool is available, output a diagram prompt generated from paper evidence.

Generated diagrams must be clearly captioned as `根据论文内容绘制的解释性示意图`. They must not contain unsupported boxes, arrows, stages, datasets, modules, or claims.

Use `references/visual_policy.md` and, when useful:

```bash
scripts/build_diagram_prompt.py evidence.md --diagram-type architecture --out diagram_prompt.md
```

For tables, run or adapt:

```bash
scripts/extract_tables.py paper.pdf --out-dir tables --metadata tables/metadata.json
```

Use cropped table images for main results and important ablations, then explain what claim the table supports in prose. Do not replace experimental analysis with a table dump.

## Output Defaults

- Language: Chinese by default, preserving English technical terms when more precise.
- Format: Markdown by default.
- Create `report.md` by default when working in a filesystem workspace.
- Include original figures or generated diagrams inline where they help explain the paper.
- Include cropped original result/ablation tables where they materially support the paper's claims.
- Do not include raw extraction logs, figure metadata dumps, or evidence-index tables in the final report unless requested.
- Do not create standalone terminology, formula-analysis, or figure-reading sections by default. Integrate terminology, formulas, algorithms, and figures into the corresponding conceptual section.
- Avoid meta-report phrasing about the report's writing choices. Captions should directly explain the paper content.
- Avoid reports that read like Chinese translations of the paper. The report should teach the paper's internal logic.
- Keep the report concrete: architecture, terminology, evidence, experiments, and limitations should be more detailed than the high-level summary.
- Use code blocks for key flows when they improve understanding: training steps, inference steps, attention masks, loss computation, data construction, retrieval/routing, or evaluation.
