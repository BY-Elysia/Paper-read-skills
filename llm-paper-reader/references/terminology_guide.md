# Terminology Guide

Use this guide when the paper introduces named modules, objectives, datasets, metrics, algorithms, benchmarks, training stages, or paper-specific concepts.

By default, explain terminology inline at the point where the paper introduces or relies on it. Do not create a standalone terminology chapter unless the user asks for a glossary.

## Term Entry Standard

For each term, include:

- Original English term
- Chinese explanation
- Paper-specific definition
- Whether it is a new concept, renamed existing concept, dataset, benchmark, module, loss, metric, or training stage
- Why it matters in the paper
- First definition or key occurrence anchor for internal grounding

## Grounding Rules

- Prefer the paper's own definition over generic textbook meaning.
- If the term is not explicitly defined, say `原文未明确给出定义` and infer only from nearby usage.
- If the paper reuses a common term with a special meaning, explain the difference.
- Do not translate proper names in a way that hides the original English term.
- Include short original-text quotes only for definitions or important claims.

## Optional Glossary Format

Use this only when the user asks for a glossary or when the report would otherwise become unreadable.

| Term | 中文解释 | 论文中的定义或用法 | 类型 | 重要性 |
|---|---|---|---|---|

## Useful Questions

- Is this term a module name or a process name?
- Does the paper define it formally, visually, or only through examples?
- Does it appear in a figure, equation, algorithm, or experiment table?
- Is it required to understand the architecture or only part of evaluation?
- Does the term hide an assumption about data, supervision, prompts, or inference?
