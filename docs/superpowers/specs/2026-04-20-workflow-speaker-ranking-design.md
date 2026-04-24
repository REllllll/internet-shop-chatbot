# Workflow Speaker Ranking Design

## Goal

Fix the recommendation workflow so speaker queries stop surfacing cable and accessory products ahead of actual speakers.

## Scope

This change covers:

- updating the `n8n` workflow ranking logic
- preserving the existing broad query step so recall does not collapse
- adding a workflow contract regression test
- validating the live browser flow after redeploying the workflow

This change does not remove the backend relevance guard that was added as protection against bad workflow output.

## Root Cause

The current `Rank Products` node boosts any product that mentions a keyword like `speaker` in `product_name` or `about_product`, then multiplies by popularity. That allows accessories such as audio cables and unrelated products such as smartwatches to outrank actual speakers if they contain the word `speaker` and have higher review counts.

## Options

### Option 1: Replace the workflow ranker with backend-style scoring

Use a more structured score that:

- rewards speaker-related category paths
- rewards keyword hits in `product_name` and `category` more than `about_product`
- includes `use_case` terms
- penalizes obvious accessory categories

Pros:

- fixes the actual ranking bug
- keeps broad candidate retrieval
- aligns workflow behavior with the backend’s better results

Cons:

- more ranking logic in the workflow code node

### Option 2: Add hardcoded boosts only for speaker categories

Pros:

- smallest workflow change

Cons:

- brittle
- still leaves other noisy categories too competitive

### Option 3: Narrow the query step to speaker-only categories

Pros:

- high precision

Cons:

- lower recall
- depends on user category wording being exact

### Recommendation

Use Option 1. The query stage should remain broad, and the ranking stage should decide relevance using stronger category-aware signals.

## Implementation

1. Update the `Rank Products` node in `workflows/recommendation-pipeline.json`.
2. Tokenize `keywords` and `use_case`.
3. Add strong positive weights for categories such as `speakers`, `bluetoothspeakers`, and `outdoorspeakers`.
4. Weight matches in `product_name` and `category` above matches in `about_product`.
5. Add negative weights for obvious accessory categories such as `cables`, `adapters`, `receivers`, and for unrelated device classes such as `smartwatches`.
6. Keep the `Build Comparison` node unchanged.
7. Add a workflow contract test to assert the new ranking code includes speaker-category preference and accessory penalties.
8. Rebuild or restart the running stack so `n8n` serves the updated workflow, then retest the Chrome flow.

## Risks

- Over-penalizing categories could hide edge-case speaker accessories that are actually desired.
- Keeping penalties targeted to clearly irrelevant categories avoids overfitting.

## Success Criteria

- A Bluetooth speaker query surfaces actual speaker products, not cables.
- The browser UI shows speaker recommendations for the existing test query.
- Workflow contract tests pass after the ranking logic change.
