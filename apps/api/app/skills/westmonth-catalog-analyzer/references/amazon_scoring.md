# Amazon Scoring Reference

Use these heuristics when analyzing WestMonth catalog products for Amazon launch potential. Scores are directional unless supplemented by live marketplace research.

## Opportunity Score

Start at 50.

Add:
- +20 for strong keyword/category match to the user's opportunity.
- +10 for lightweight, compact products.
- +10 for evergreen demand categories: kitchen, home, beauty tools, fitness accessories, pet, office, travel.
- +10 for variants that can support listing options.
- +5 for clear product images and detailed descriptions.

Subtract:
- -10 for unclear product identity or weak description.
- -10 for bulky, heavy, or hard-to-ship items.
- -15 for products with obvious brand/trademark dependency.
- -20 for regulated categories requiring strong compliance proof.

## Risk Score

Start at 30.

Add:
- +20 for fragile materials such as glass, ceramic, mirrors, or delicate electronics.
- +20 for batteries, ingestibles, cosmetics, medical claims, toys for children, or electrical safety concerns.
- +15 for trademark, character, sports team, celebrity, or branded compatibility terms.
- +15 for oversized, heavy, liquid, sharp, magnetic, or temperature-sensitive products.
- +10 for strongly seasonal products.

Subtract:
- -10 for simple non-electronic accessories.
- -10 for compact durable goods with low breakage risk.

## Margin Score

If cost is available, estimate margin from suggested selling price minus cost, marketplace fee buffer, and FBA/shipping buffer.

If only WestMonth price is available, treat that price as a conservative proxy for landed product cost and label the margin as an estimate.

Suggested selling price:
- Use 1.8x to 2.5x catalog price for low-priced lightweight goods.
- Use 1.5x to 2.0x catalog price for mid-priced goods.
- Use 1.3x to 1.7x catalog price for bulky or fragile goods.

Margin Score guide:
- 80-100: estimated gross margin above 45%.
- 60-79: estimated gross margin around 35-45%.
- 40-59: estimated gross margin around 25-35%.
- 0-39: estimated gross margin below 25% or unknown with poor pricing leverage.

## Compliance Watchlist

Treat these categories as higher risk until documentation is available:
- Cosmetics, skincare, supplements, food contact claims, medical or therapeutic products.
- Toys, baby products, children's products.
- Electronics, batteries, chargers, heated products, LED products.
- Branded, licensed, patented, character-based, or compatibility-dependent products.

## Action Selection

Use `Launch Immediately` only when product fit, margin, and risk are all favorable.

Use `Further Research` when the product is promising but needs Amazon demand validation, compliance documents, or competitor checks.

Use `Avoid` when the product has high compliance risk, poor margin, weak fit, or likely trademark/IP exposure.
