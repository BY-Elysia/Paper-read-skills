# Formula Explanation

Use this guide whenever a paper contains equations, losses, algorithms, scores, update rules, metrics, routing rules, attention formulas, optimization objectives, or probability definitions.

## Standard

For each important formula, explain these things:

1. **Purpose**: what quantity the formula computes and why the paper needs it.
2. **Symbols**: every important symbol, including index ranges and tensor shapes when available.
3. **Computation**: how the value is calculated step by step.
4. **Location in the method**: whether it belongs to data construction, model forward pass, training loss, inference, intervention, or evaluation.
5. **Intuition**: what the formula is doing in plain language.
6. **Assumptions and limits**: what the formula assumes, ignores, or makes fragile.
7. **Implementation details**: when relevant, specify softmax axis, mask semantics, positive/negative samples, normalization, temperature, logits, pooling/averaging/max/top-k, and which parameters receive gradients.

## Explanation Pattern

Avoid saying only “the paper defines X as...”. Teach the formula:

```markdown
这里作者要计算的是 <quantity>，它用于 <method role>。

$$
...
$$

这个式子可以分成几步理解。第一步，...；第二步，...；第三步，...。
其中，... 表示 ...，维度是 ...；... 表示 ...。
直观上，它是在 ...。如果 <condition> 不成立，这个公式可能会 ...
```

## Depth Rules

- Attention formulas: explain Q, K, V, mask, softmax axis, score matrix shape, and what is read/written.
- Loss functions: explain each term, supervision signal, optimization direction, and trade-off coefficients.
- Similarity scores: explain the compared objects, vector dimensions, normalization, dot product or cosine computation, temperature if present, and how multiple scores are pooled.
- Contrastive objectives: explain positive/negative samples, score matrix shape, score function, normalization, softmax axis, and what representation is being separated.
- RL/preference objectives: explain policy, reference model, reward/preference signal, KL or regularization terms, and update target.
- Routing/retrieval scores: explain candidates, scoring function, top-k or threshold selection, and how selected items affect later modules.
- Evaluation metrics: explain numerator/denominator, higher/lower better, and what claim the metric can or cannot support.

## Pseudocode

When formulas define a process rather than a single scalar, add a compact pseudocode block after the explanation. Good candidates include:

- one training step
- one inference step
- attention mask construction
- negative sampling or reranking
- retrieval/routing candidate selection
- reward or preference optimization update

Pseudocode must use paper-grounded names. If a line depends on an implementation detail not stated in the paper, mark it as `原文未明确说明` or phrase it as an implementation assumption.

Do not use an undefined paper-specific function as a substitute for explaining a formula or mechanism. Expand important scoring, attention, routing, retrieval, loss, or update functions until the actual computation is visible.

## Placement

Explain formulas where the corresponding mechanism appears in the report. Do not collect all formulas into a standalone formula section unless the user explicitly asks.
