"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { Bookmark, ExternalLink, ShieldAlert } from "lucide-react";
import { api, Opportunity, scoreColor } from "@/lib/api";
import { PageTitle, Shell, Stat } from "@/components/Shell";

type Evidence = { id: number; source_name: string; source_url: string | null; summary: string; confidence: string };

export default function ProductDetailPage() {
  const params = useParams<{ id: string }>();
  const [item, setItem] = useState<Opportunity | null>(null);
  const [evidence, setEvidence] = useState<Evidence[]>([]);

  useEffect(() => {
    api<Opportunity>(`/opportunities/${params.id}`).then(setItem);
    api<Evidence[]>(`/opportunities/${params.id}/evidence`).then(setEvidence);
  }, [params.id]);

  if (!item) return <Shell><PageTitle title="加载中" subtitle="正在读取机会详情。" /></Shell>;

  return (
    <Shell>
      <PageTitle title={item.title} subtitle={`${item.category ?? "未分类"} · ${item.recommended_action} · ${item.confidence} confidence`} />
      <div className="grid gap-4 md:grid-cols-5">
        <Stat label="机会评分" value={String(item.opportunity_score)} tone={scoreColor(item.opportunity_score)} />
        <Stat label="需求" value={String(item.demand_score)} />
        <Stat label="利润" value={String(item.margin_score)} />
        <Stat label="竞品进入" value={String(item.competition_score)} />
        <Stat label="货盘匹配" value={String(item.catalog_match_score)} />
      </div>
      <section className="mt-5 grid gap-4 lg:grid-cols-[1.4fr_.8fr]">
        <div className="rounded-md border border-line bg-white p-4">
          <h2 className="text-sm font-semibold">分析报告</h2>
          <dl className="mt-4 grid gap-4 text-sm md:grid-cols-2">
            <Field label="人群画像" value={item.target_audience} />
            <Field label="生命周期" value={item.lifecycle_stage} />
            <Field label="季节性" value={item.seasonality} />
            <Field label="上架难度" value={item.listing_difficulty} />
            <Field label="风险等级" value={item.risk_level} danger={item.risk_level === "高"} />
            <Field label="差异化点" value={item.differentiation} />
          </dl>
          <div className="mt-5">
            <h3 className="text-sm font-semibold">Top 产品特征优势</h3>
            <div className="mt-2 flex flex-wrap gap-2">
              {(item.top_features ?? []).map((feature) => (
                <span key={feature} className="rounded-md border border-line px-3 py-1 text-sm">{feature}</span>
              ))}
            </div>
          </div>
        </div>
        <div className="rounded-md border border-line bg-white p-4">
          <h2 className="flex items-center gap-2 text-sm font-semibold"><ShieldAlert size={16} /> 风险审查</h2>
          <div className={`mt-3 rounded-md p-3 text-sm ${item.risk_level === "高" ? "bg-red-50 text-danger" : "bg-panel text-slate-700"}`}>
            高风险产品默认不推荐上架；商标、专利、限制品类和合规文件需要人工确认。
          </div>
          <button className="mt-4 flex w-full items-center justify-center gap-2 rounded-md border border-line px-3 py-2 text-sm" onClick={() => api(`/opportunities/${item.id}/save`, { method: "POST", body: JSON.stringify({ status: "watching" }) })}>
            <Bookmark size={16} />
            收藏机会
          </button>
        </div>
      </section>
      <section className="mt-5 rounded-md border border-line bg-white p-4">
        <h2 className="text-sm font-semibold">证据与来源</h2>
        <div className="mt-3 divide-y divide-line">
          {evidence.map((row) => (
            <div key={row.id} className="flex items-start justify-between gap-4 py-3 text-sm">
              <div>
                <div className="font-medium">{row.source_name} · {row.confidence}</div>
                <p className="mt-1 text-slate-600">{row.summary}</p>
              </div>
              {row.source_url ? <a className="text-brand" href={row.source_url} target="_blank"><ExternalLink size={16} /></a> : null}
            </div>
          ))}
        </div>
      </section>
    </Shell>
  );
}

function Field({ label, value, danger }: { label: string; value?: string | null; danger?: boolean }) {
  return (
    <div>
      <dt className="text-xs text-slate-500">{label}</dt>
      <dd className={`mt-1 ${danger ? "font-semibold text-danger" : "text-slate-800"}`}>{value ?? "待确认"}</dd>
    </div>
  );
}
