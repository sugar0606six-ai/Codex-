#!/usr/bin/env python3
"""WestMonth catalog ingestion, search, and Amazon opportunity analysis."""

from __future__ import annotations

import argparse
import html
import json
import math
import os
import re
import sys
import time
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

BASE_URL = "https://www.westmonth.com"
ALL_PRODUCTS_URL = f"{BASE_URL}/products/all"
DEFAULT_MEMORY = (
    Path.home()
    / ".codex"
    / "memories"
    / "westmonth-catalog-analyzer"
    / "catalog.json"
)


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "a":
            return
        attr = dict(attrs)
        href = attr.get("href")
        if href:
            self.links.append(href)


def fetch_text(url: str, timeout: int = 25) -> str:
    req = Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (compatible; WestMonthCatalogAnalyzer/1.0)",
            "Accept": "text/html,application/json;q=0.9,*/*;q=0.8",
        },
    )
    with urlopen(req, timeout=timeout) as response:
        raw = response.read()
        charset = response.headers.get_content_charset() or "utf-8"
    return raw.decode(charset, errors="replace")


def normalize_text(value: Any) -> str:
    text = html.unescape(re.sub(r"<[^>]+>", " ", str(value or "")))
    return re.sub(r"\s+", " ", text).strip()


def parse_price(value: Any) -> float | None:
    if value in (None, ""):
        return None
    if isinstance(value, (int, float)):
        number = float(value)
        return round(number / 100, 2) if number > 1000 else round(number, 2)
    match = re.search(r"(\d+(?:\.\d+)?)", str(value).replace(",", ""))
    return round(float(match.group(1)), 2) if match else None


def grams_to_weight(grams: Any) -> dict[str, float] | None:
    try:
        value = float(grams)
    except (TypeError, ValueError):
        return None
    if value <= 0:
        return None
    return {"grams": round(value, 1), "lb": round(value / 453.59237, 2)}


def extract_dimensions(text: str) -> str | None:
    patterns = [
        r"(\d+(?:\.\d+)?\s*[xX*]\s*\d+(?:\.\d+)?\s*[xX*]\s*\d+(?:\.\d+)?\s*(?:cm|mm|in|inch|inches)?)",
        r"(?:size|dimensions?)[:\s]+([^.;\n]{3,80})",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.I)
        if match:
            return normalize_text(match.group(1))
    return None


def product_handles(limit_pages: int = 200) -> list[str]:
    handles: list[str] = []
    seen: set[str] = set()
    empty_pages = 0
    for page in range(1, limit_pages + 1):
        url = f"{ALL_PRODUCTS_URL}?page={page}"
        try:
            body = fetch_text(url)
        except Exception:
            break
        parser = LinkParser()
        parser.feed(body)
        before = len(handles)
        for href in parser.links:
            parsed = urlparse(href)
            path = parsed.path
            match = re.match(r"^/products/([^/?#]+)$", path)
            if not match:
                continue
            handle = match.group(1)
            if handle and handle != "all" and handle not in seen:
                seen.add(handle)
                handles.append(handle)
        empty_pages = empty_pages + 1 if len(handles) == before else 0
        if empty_pages >= 2:
            break
    return handles


def load_product(handle: str) -> dict[str, Any]:
    product_url = f"{BASE_URL}/products/{handle}"
    json_url = f"{product_url}.js"
    raw_json: dict[str, Any] = {}
    page_text = ""
    try:
        raw_json = json.loads(fetch_text(json_url))
    except Exception:
        page_text = fetch_text(product_url)
    if not page_text:
        try:
            page_text = fetch_text(product_url)
        except Exception:
            page_text = ""

    description = normalize_text(raw_json.get("description") or page_text)
    variants = []
    skus = []
    prices = []
    weights = []
    inventory_values = []

    for variant in raw_json.get("variants", []) or []:
        sku = normalize_text(variant.get("sku"))
        price = parse_price(variant.get("price"))
        weight = grams_to_weight(variant.get("grams"))
        available = variant.get("available")
        if sku:
            skus.append(sku)
        if price is not None:
            prices.append(price)
        if weight:
            weights.append(weight)
        if available is not None:
            inventory_values.append(bool(available))
        variants.append(
            {
                "id": variant.get("id"),
                "title": normalize_text(variant.get("title")),
                "sku": sku or None,
                "price": price,
                "available": available,
                "weight": weight,
                "options": [normalize_text(v) for v in variant.get("options", [])],
            }
        )

    title = normalize_text(raw_json.get("title")) or infer_title(page_text, handle)
    category = normalize_text(raw_json.get("type")) or infer_category(page_text)
    images = raw_json.get("images") or extract_images(page_text, product_url)
    tags = [normalize_text(tag) for tag in raw_json.get("tags", []) if normalize_text(tag)]

    return {
        "handle": handle,
        "url": product_url,
        "product_name": title,
        "sku": skus[0] if skus else None,
        "skus": skus,
        "category": category or None,
        "price": min(prices) if prices else parse_price(page_text),
        "cost": None,
        "weight": min(weights, key=lambda item: item["grams"]) if weights else None,
        "dimensions": extract_dimensions(description),
        "product_description": description[:4000],
        "images": images,
        "variants": variants,
        "inventory_information": (
            "available" if any(inventory_values) else "unavailable" if inventory_values else "unknown"
        ),
        "tags": tags,
        "source": "westmonth",
        "last_indexed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }


def infer_title(page_text: str, handle: str) -> str:
    match = re.search(r"<title[^>]*>(.*?)</title>", page_text, flags=re.I | re.S)
    if match:
        return normalize_text(match.group(1).split("|")[0])
    return handle.replace("-", " ").title()


def infer_category(page_text: str) -> str | None:
    match = re.search(r"(?:category|product_type)[\"'\s:]+([^\"'<>,]{2,80})", page_text, flags=re.I)
    return normalize_text(match.group(1)) if match else None


def extract_images(page_text: str, product_url: str) -> list[str]:
    urls = re.findall(r"https?://[^\"']+\.(?:jpg|jpeg|png|webp)", page_text, flags=re.I)
    relative = re.findall(r"(//[^\"']+\.(?:jpg|jpeg|png|webp))", page_text, flags=re.I)
    combined = urls + [f"https:{item}" for item in relative]
    cleaned = []
    seen = set()
    for url in combined:
        full = urljoin(product_url, html.unescape(url))
        if full not in seen:
            seen.add(full)
            cleaned.append(full)
    return cleaned[:20]


def save_catalog(products: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "source": ALL_PRODUCTS_URL,
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "product_count": len(products),
        "products": products,
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def load_catalog(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        raise SystemExit(f"Catalog memory not found: {path}. Run ingest first.")
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload.get("products", [])


def tokens(text: str) -> set[str]:
    return {item for item in re.findall(r"[a-z0-9]+", text.lower()) if len(item) > 1}


def product_blob(product: dict[str, Any]) -> str:
    fields = [
        product.get("product_name"),
        product.get("sku"),
        product.get("category"),
        product.get("product_description"),
        " ".join(product.get("tags") or []),
    ]
    return " ".join(normalize_text(item) for item in fields if item)


def similarity(query: str, product: dict[str, Any]) -> int:
    query_tokens = tokens(query)
    if not query_tokens:
        return 0
    product_tokens = tokens(product_blob(product))
    overlap = len(query_tokens & product_tokens)
    score = overlap / max(len(query_tokens), 1)
    name_bonus = 0.15 if query.lower() in normalize_text(product.get("product_name")).lower() else 0
    return min(100, round((score + name_bonus) * 100))


def is_lightweight(product: dict[str, Any]) -> bool:
    weight = product.get("weight") or {}
    grams = weight.get("grams")
    return grams is None or grams <= 907


def risk_terms(product: dict[str, Any]) -> set[str]:
    text = product_blob(product)
    found = set()
    for term in [
        "battery",
        "electric",
        "glass",
        "ceramic",
        "cosmetic",
        "skin",
        "medical",
        "baby",
        "toy",
        "led",
        "charger",
        "knife",
        "magnetic",
        "liquid",
        "disney",
        "nike",
        "apple",
        "pokemon",
    ]:
        if re.search(rf"\b{re.escape(term)}\b", text, flags=re.I):
            found.add(term)
    return found


def score_product(product: dict[str, Any], query: str = "") -> dict[str, Any]:
    sim = similarity(query, product) if query else 50
    price = product.get("cost") or product.get("price")
    price = float(price) if price else None
    lightweight = is_lightweight(product)
    risky = risk_terms(product)
    category_text = normalize_text(product.get("category")).lower()

    opportunity = 45 + round(sim * 0.35)
    if lightweight:
        opportunity += 10
    if any(term in category_text for term in ["kitchen", "home", "beauty", "fitness", "pet", "office", "travel"]):
        opportunity += 10
    if len(product.get("variants") or []) > 1:
        opportunity += 5
    if product.get("images"):
        opportunity += 5
    if risky:
        opportunity -= min(20, len(risky) * 5)

    risk = 30 + len(risky) * 12
    if not lightweight:
        risk += 15
    if product.get("dimensions") is None:
        risk += 5
    risk = clamp(risk)

    if price:
        multiplier = 2.2 if lightweight and price < 20 else 1.8 if lightweight else 1.5
        suggested = round(max(price * multiplier, price + 8), 2)
        fee_buffer = suggested * 0.22
        fulfillment_buffer = 5 if lightweight else 12
        estimated_margin = round((suggested - price - fee_buffer - fulfillment_buffer) / suggested * 100, 1)
        margin_score = clamp(round(estimated_margin * 1.8))
    else:
        suggested = None
        estimated_margin = None
        margin_score = 35

    opportunity = clamp(opportunity)
    margin_score = clamp(margin_score)
    if opportunity >= 75 and risk <= 40 and margin_score >= 60:
        action = "Launch Immediately"
    elif risk >= 75 or margin_score < 35:
        action = "Avoid"
    else:
        action = "Further Research"

    return {
        "similarity_score": sim,
        "estimated_amazon_demand": demand_label(opportunity),
        "suggested_selling_price": suggested,
        "estimated_margin_percent": estimated_margin,
        "opportunity_score": opportunity,
        "risk_score": risk,
        "margin_score": margin_score,
        "risk_flags": sorted(risky),
        "fba_suitability": "High" if lightweight and risk <= 45 else "Medium" if risk <= 65 else "Low",
        "shipping_complexity": "Low" if lightweight else "Medium",
        "fragility": "Potential" if risky & {"glass", "ceramic"} else "Low/unknown",
        "seasonality": "Unknown; validate with marketplace data",
        "trademark_risk": "Potential" if risky & {"disney", "nike", "apple", "pokemon"} else "Low/unknown",
        "compliance_risk": "Potential" if risky & {"battery", "electric", "cosmetic", "skin", "medical", "baby", "toy", "led", "charger"} else "Low/unknown",
        "recommended_action": action,
    }


def clamp(value: float) -> int:
    return max(0, min(100, int(round(value))))


def demand_label(score: int) -> str:
    if score >= 75:
        return "High heuristic estimate"
    if score >= 55:
        return "Medium heuristic estimate"
    return "Low heuristic estimate"


def markdown_report(product: dict[str, Any], scores: dict[str, Any]) -> str:
    price = product.get("price")
    cost_note = product.get("cost") if product.get("cost") is not None else "Unavailable; price used as conservative proxy when needed"
    lines = [
        "# Product Summary",
        "",
        f"- Product Name: {product.get('product_name') or 'Unknown'}",
        f"- SKU: {product.get('sku') or ', '.join(product.get('skus') or []) or 'Unknown'}",
        f"- Category: {product.get('category') or 'Unknown'}",
        f"- Price: {price if price is not None else 'Unknown'}",
        f"- Cost: {cost_note}",
        f"- Weight: {product.get('weight') or 'Unknown'}",
        f"- Dimensions: {product.get('dimensions') or 'Unknown'}",
        f"- Inventory: {product.get('inventory_information') or 'Unknown'}",
        f"- URL: {product.get('url')}",
        "",
        "# Catalog Match",
        "",
        f"- Similarity Score: {scores['similarity_score']}/100",
        f"- Estimated Amazon Demand: {scores['estimated_amazon_demand']}",
        f"- Variants: {len(product.get('variants') or [])}",
        "",
        "# Amazon Suitability",
        "",
        f"- FBA Suitability: {scores['fba_suitability']}",
        f"- Shipping Complexity: {scores['shipping_complexity']}",
        f"- Fragility: {scores['fragility']}",
        f"- Seasonality: {scores['seasonality']}",
        f"- Trademark Risk: {scores['trademark_risk']}",
        f"- Compliance Risk: {scores['compliance_risk']}",
        f"- Opportunity Score: {scores['opportunity_score']}/100",
        f"- Risk Score: {scores['risk_score']}/100",
        "",
        "# Margin Estimate",
        "",
        f"- Suggested Selling Price: {scores['suggested_selling_price'] if scores['suggested_selling_price'] is not None else 'Unknown'}",
        f"- Estimated Margin: {scores['estimated_margin_percent'] if scores['estimated_margin_percent'] is not None else 'Unknown'}%",
        f"- Margin Score: {scores['margin_score']}/100",
        "",
        "# Recommended Action",
        "",
        scores["recommended_action"],
    ]
    return "\n".join(lines)


def command_ingest(args: argparse.Namespace) -> None:
    handles = product_handles(args.limit_pages)
    products = []
    for index, handle in enumerate(handles[: args.limit_products or None], start=1):
        print(f"[{index}/{len(handles)}] {handle}", file=sys.stderr)
        try:
            products.append(load_product(handle))
        except Exception as exc:
            print(f"Warning: failed to index {handle}: {exc}", file=sys.stderr)
    save_catalog(products, Path(args.catalog))
    print(f"Indexed {len(products)} products into {args.catalog}")


def filtered_products(products: list[dict[str, Any]], args: argparse.Namespace) -> list[dict[str, Any]]:
    results = products
    if args.keyword:
        needle = args.keyword.lower()
        results = [p for p in results if needle in product_blob(p).lower()]
    if args.category:
        needle = args.category.lower()
        results = [p for p in results if needle in normalize_text(p.get("category")).lower()]
    if args.lightweight:
        results = [p for p in results if is_lightweight(p)]
    scored = [(p, score_product(p, args.keyword or args.category or "")) for p in results]
    if args.fba_suitable:
        scored = [(p, s) for p, s in scored if s["fba_suitability"] in {"High", "Medium"}]
    if args.high_margin:
        scored = [(p, s) for p, s in scored if s["margin_score"] >= 60]
    scored.sort(key=lambda pair: (pair[1]["opportunity_score"], pair[1]["margin_score"]), reverse=True)
    return [p for p, _ in scored[: args.limit]]


def command_search(args: argparse.Namespace) -> None:
    products = filtered_products(load_catalog(Path(args.catalog)), args)
    if args.markdown and products:
        product = products[0]
        print(markdown_report(product, score_product(product, args.keyword or args.category or "")))
        return
    print(json.dumps(products, ensure_ascii=False, indent=2))


def command_match(args: argparse.Namespace) -> None:
    products = load_catalog(Path(args.catalog))
    ranked = sorted(products, key=lambda product: similarity(args.query, product), reverse=True)
    for product in ranked[: args.limit]:
        scores = score_product(product, args.query)
        if args.markdown:
            print(markdown_report(product, scores))
            if args.limit > 1:
                print("\n---\n")
        else:
            print(json.dumps({"product": product, "analysis": scores}, ensure_ascii=False, indent=2))


def command_sku(args: argparse.Namespace) -> None:
    sku = args.sku.lower()
    products = load_catalog(Path(args.catalog))
    for product in products:
        skus = [normalize_text(product.get("sku")).lower()] + [s.lower() for s in product.get("skus") or []]
        if sku in skus:
            print(markdown_report(product, score_product(product, product.get("product_name") or "")))
            return
    raise SystemExit(f"SKU not found: {args.sku}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", default=os.environ.get("WESTMONTH_CATALOG_PATH", str(DEFAULT_MEMORY)))
    sub = parser.add_subparsers(dest="command", required=True)

    ingest = sub.add_parser("ingest", help="Crawl WestMonth and persist catalog memory.")
    ingest.add_argument("--limit-pages", type=int, default=200)
    ingest.add_argument("--limit-products", type=int, default=0)
    ingest.set_defaults(func=command_ingest)

    search = sub.add_parser("search", help="Search the persisted catalog.")
    search.add_argument("--keyword")
    search.add_argument("--category")
    search.add_argument("--lightweight", action="store_true")
    search.add_argument("--fba-suitable", action="store_true")
    search.add_argument("--high-margin", action="store_true")
    search.add_argument("--limit", type=int, default=10)
    search.add_argument("--markdown", action="store_true")
    search.set_defaults(func=command_search)

    match = sub.add_parser("match", help="Match a market opportunity to catalog products.")
    match.add_argument("--query", required=True)
    match.add_argument("--limit", type=int, default=3)
    match.add_argument("--markdown", action="store_true", default=True)
    match.set_defaults(func=command_match)

    sku = sub.add_parser("sku", help="Look up a product by SKU.")
    sku.add_argument("--sku", required=True)
    sku.set_defaults(func=command_sku)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
