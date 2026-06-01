"use client";

import { useState } from "react";
import Link from "next/link";
import { Play, Search } from "lucide-react";
import { api, Opportunity, scoreColor } from "@/lib/api";
import { PageTitle, Shell } from "@/components/Shell";

export default function SearchPage() {
  const [keywords, setKeywords] = useState("microfiber cleaning brush\ncar trunk organizer");
  const [category, setCategory] = useState("Home & Kitchen");
  const [loading, setLoading] = useState(false);
  const [items, setItems] = useState<Opportunity[]>([]);

  async function run() {
    setLoading(true);
    const list = keywords.split(/\n|,/).map((item) => item.trim()).filter(Boolean);
    try {
      const result = await api<Opportunity[]>("/opportunities/analyze", {
        method: "POST",
        body: JSON.stringify({ keywords: list, category })
      });
      setItems(result);
    } finally {
      setLoading(false);
    }
  }

  return (
    <Shell>
      <PageTitle title="关键词 / 批量搜索" subtitle="输入产品词后自动执行趋势、利润、竞品、WestMonth 匹配和风险评分。" />
      <section className="rounded-md border border-line bg-white p-4">
        <div className="grid gap-4 lg:grid-cols-[1fr_240px]">
          <textarea className="focus-ring min-h-36 rounded-md border border-line p-3 text-sm" value={keywords} onChange={(e) => setKeywords(e.target.value)} />
          <div>
            <label className="text-sm font-medium">主类目</label>
            <select className="focus-ring mt-2 w-full rounded-md border border-line px-3 py-2 text-sm" value={category} onChange={(e) => setCategory(e.target.value)}>
              <option>Home & Kitchen</option>
              <option>Automotive</option>
              <option>Health & Household</option>
            </select>
            <button onClick={run} disabled={loading} className="focus-ring mt-4 flex w-full items-center justify-center gap-2 rounded-md bg-brand px-4 py-2 text-sm font-semibold text-white disabled:opacity-60">
              {loading ? <Search size={16} /> : <Play size={16} />}
              {loading ? "分析中" : "开始分析"}
            </button>
          </div>
        </div>
      </section>
      {items.length ? (
        <section className="mt-5 grid gap-3 md:grid-cols-2">
          {items.map((item) => (
            <Link href={`/products/${item.id}`} key={item.id} className="rounded-md border border-line bg-white p-4 hover:border-brand">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <h2 className="font-semibold">{item.title}</h2>
                  <p className="mt-1 text-sm text-slate-600">{item.category}</p>
                </div>
                <div className={`text-2xl font-semibold ${scoreColor(item.opportunity_score)}`}>{item.opportunity_score}</div>
              </div>
              <div className="mt-4 grid grid-cols-4 gap-2 text-center text-xs">
                <Metric label="需求" value={item.demand_score} />
                <Metric label="利润" value={item.margin_score} />
                <Metric label="竞品" value={item.competition_score} />
                <Metric label="库存" value={item.catalog_match_score} />
              </div>
              <div className="mt-4 flex items-center justify-between text-sm">
                <span className={item.risk_level === "高" ? "text-danger" : "text-slate-600"}>风险：{item.risk_level}</span>
                <span className="font-medium">{item.recommended_action}</span>
              </div>
            </Link>
          ))}
        </section>
      ) : null}
    </Shell>
  );
}

function Metric({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded-md bg-panel p-2">
      <div className="text-slate-500">{label}</div>
      <div className="mt-1 font-semibold">{value}</div>
    </div>
  );
}
