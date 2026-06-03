---
name: westmonth-catalog-analyzer
description: Internal catalog intelligence for WestMonth inventory. Use when users mention WestMonth, our catalog, our products, company inventory, SKU lookup, catalog ingestion, product matching, Amazon FBA suitability, product opportunity scoring, margin analysis, or finding existing WestMonth products to launch on Amazon. Crawls https://www.westmonth.com/products/all, persists a searchable catalog knowledge base, and returns product summaries, catalog matches, Amazon suitability, margin estimates, and recommended launch actions.
---

# WestMonth Catalog Analyzer

## Overview

Use this skill as the internal catalog intelligence engine for WestMonth. It ingests the WestMonth product catalog, persists a searchable local knowledge base, and analyzes products for Amazon launch fit.

Primary source: `https://www.westmonth.com/products/all`

Persistent memory location: `C:\Users\205129\.codex\memories\westmonth-catalog-analyzer\catalog.json`

## Default Workflow

1. For any request mentioning `our catalog`, `our products`, `company inventory`, `WestMonth`, SKU lookup, Amazon suitability, or product matching, automatically use the persisted WestMonth catalog knowledge base.
2. If the local catalog is missing, stale, or the user asks to refresh, run `scripts/catalog_tool.py ingest`.
3. For SKU or exact product lookup, run `scripts/catalog_tool.py sku --sku <SKU>` or search by product name.
4. For market opportunity matching, run `scripts/catalog_tool.py match --query "<opportunity>"`.
5. For category, keyword, weight, FBA, or margin research, run `scripts/catalog_tool.py search` with the relevant filters.
6. Return the required output sections exactly:
   - `# Product Summary`
   - `# Catalog Match`
   - `# Amazon Suitability`
   - `# Margin Estimate`
   - `# Recommended Action`

## Catalog Ingestion

Use:

```bash
python scripts/catalog_tool.py ingest
```

The ingestion script crawls product pages from WestMonth, tries Shopify-style product JSON endpoints when available, and extracts:

- Product Name
- SKU
- Category
- Price
- Cost, only if available in source data
- Weight
- Dimensions
- Product Description
- Images
- Variants
- Inventory Information

If cost, dimensions, or inventory are unavailable, preserve them as `null` or `unknown`; do not invent them.

## Query Patterns

Use `search` for catalog exploration:

```bash
python scripts/catalog_tool.py search --keyword "blender"
python scripts/catalog_tool.py search --category "Kitchen"
python scripts/catalog_tool.py search --lightweight
python scripts/catalog_tool.py search --fba-suitable
python scripts/catalog_tool.py search --high-margin
```

Use `match` for market opportunities:

```bash
python scripts/catalog_tool.py match --query "Portable Blender"
```

Use `sku` for direct SKU lookup:

```bash
python scripts/catalog_tool.py sku --sku "ABC-123"
```

## Scoring Rules

Read `references/amazon_scoring.md` before changing scoring logic or explaining a borderline score.

Score each matched product from 0-100:

- `Opportunity Score`: catalog relevance plus estimated Amazon launch appeal.
- `Risk Score`: shipping complexity, fragility, seasonality, trademark, and compliance risk.
- `Margin Score`: estimated spread between WestMonth price or cost and suggested Amazon selling price.

Recommended action thresholds:

- `Launch Immediately`: Opportunity >= 75, Risk <= 40, Margin >= 60.
- `Further Research`: Opportunity >= 50 or Margin >= 45, unless Risk >= 75.
- `Avoid`: Risk >= 75, Margin < 35, or obvious compliance/trademark concerns.

## Output Contract

Always return Markdown with these sections:

```markdown
# Product Summary

# Catalog Match

# Amazon Suitability

# Margin Estimate

# Recommended Action
```

Include SKU, similarity score, estimated Amazon demand, suggested selling price, estimated margin, opportunity score, risk score, margin score, and the action. If market demand is not backed by live market data, label it as `heuristic estimate`.

## Data Integrity

- Treat the WestMonth catalog as the source of truth for internal inventory.
- Do not claim cost, dimensions, or inventory values unless extracted from source data or supplied by the user.
- Use web access only when refreshing or verifying current catalog data.
- Prefer persisted catalog memory for routine queries.
- If a user provides newer supplier sheets or internal inventory files, merge them into the catalog memory and mark their source.
