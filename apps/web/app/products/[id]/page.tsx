"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { Bookmark, ExternalLink, ShieldAlert } from "lucide-react";
import { api, Opportunity, scoreColor } from "@/lib/api";
import { PageTitle, Shell, Stat } from "@/components/Shell";

type Evidence = { id: number; source_name: string; source_url: string | null; summary: string; confidence: string };
type Competitor = {
  id: number;
  asin: string | null;
  title: string | null;
  url: string;
  price: number | null;
  rating: number | null;
  review_count: number | null;
  estimated_monthly_sales: number | null;
  image_url: string | null;
  differentiation: string | null;
};
type Profit = {
  selling_price: number;
  product_cost: number | null;
  referral_fee: number;
  fba_fee: number;
  inbound_shipping: number;
  ppc_buffer: number;
  net_margin: number;
  margin_rate: number;
  confidence: string;
};
type Trend = { id: number; source: string; window_days: number; trend_score: number; direction: string; evidence_url: string | null; confidence: string };
type OpportunityDetail = Opportunity & {
  competitors?: Competitor[];
  profit?: Profit | null;
  trends?: Trend[];
};

export default function ProductDetailPage() {
  const params = useParams<{ id: string }>();
  const [item, setItem] = useState<Opportunity | null>(null);
  const [evidence, setEvidence] = useState<Evidence[]>([]);
  const [competitors, setCompetitors] = useState<Competitor[]>([]);
  const [profit, setProfit] = useState<Profit | null>(null);
  const [trends, setTrends] = useState<Trend[]>([]);

  useEffect(() => {
    api<OpportunityDetail>(`/opportunities/${params.id}`).then((detail) => {
      setItem(detail);
      setCompetitors(detail.competitors ?? []);
      setProfit(detail.profit ?? null);
      setTrends(detail.trends ?? []);
    });
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
        <h2 className="text-sm font-semibold">Amazon US 竞品对比</h2>
        <div className="mt-3 overflow-x-auto">
          <table className="w-full min-w-[980px] text-left text-sm">
            <thead className="bg-panel text-xs uppercase text-slate-500">
              <tr>
                <th className="px-3 py-2">竞品</th>
                <th className="px-3 py-2">ASIN</th>
                <th className="px-3 py-2">价格</th>
                <th className="px-3 py-2">评分</th>
                <th className="px-3 py-2">评论</th>
                <th className="px-3 py-2">预估月销</th>
                <th className="px-3 py-2">差异化判断</th>
              </tr>
            </thead>
            <tbody>
              {competitors.map((row) => (
                <tr key={row.id} className="border-t border-line align-top">
                  <td className="px-3 py-3">
                    <a className="font-medium text-brand" href={row.url} target="_blank">{row.title ?? "Untitled"}</a>
                  </td>
                  <td className="px-3 py-3">{row.asin ?? "待确认"}</td>
                  <td className="px-3 py-3">{money(row.price)}</td>
                  <td className="px-3 py-3">{row.rating ?? "待确认"}</td>
                  <td className="px-3 py-3">{row.review_count ?? "待确认"}</td>
                  <td className="px-3 py-3">{row.estimated_monthly_sales ?? "待确认"}</td>
                  <td className="px-3 py-3 text-slate-600">{row.differentiation ?? "待确认"}</td>
                </tr>
              ))}
              {!competitors.length ? (
                <tr><td className="px-3 py-4 text-slate-500" colSpan={7}>暂无竞品数据，请先重新运行关键词分析。</td></tr>
              ) : null}
            </tbody>
          </table>
        </div>
      </section>
      <section className="mt-5 grid gap-4 lg:grid-cols-2">
        <div className="rounded-md border border-line bg-white p-4">
          <h2 className="text-sm font-semibold">利润拆解</h2>
          {profit ? (
            <dl className="mt-4 grid grid-cols-2 gap-3 text-sm">
              <Field label="主流售价" value={money(profit.selling_price)} />
              <Field label="产品成本" value={money(profit.product_cost)} />
              <Field label="平台佣金" value={money(profit.referral_fee)} />
              <Field label="FBA 费用" value={money(profit.fba_fee)} />
              <Field label="入仓运费" value={money(profit.inbound_shipping)} />
              <Field label="PPC buffer" value={money(profit.ppc_buffer)} />
              <Field label="单件净利润" value={money(profit.net_margin)} />
              <Field label="利润率" value={`${Math.round(profit.margin_rate * 1000) / 10}% · ${profit.confidence}`} />
            </dl>
          ) : <p className="mt-3 text-sm text-slate-500">暂无利润数据。</p>}
        </div>
        <div className="rounded-md border border-line bg-white p-4">
          <h2 className="text-sm font-semibold">关键词趋势</h2>
          <div className="mt-3 divide-y divide-line">
            {trends.map((row) => (
              <div key={row.id} className="flex items-center justify-between py-3 text-sm">
                <div>
                  <div className="font-medium">{row.source} · {row.window_days} 天</div>
                  <div className="text-slate-500">{row.direction} · {row.confidence}</div>
                </div>
                <div className="text-lg font-semibold">{row.trend_score}</div>
              </div>
            ))}
            {!trends.length ? <p className="py-3 text-sm text-slate-500">暂无趋势数据。</p> : null}
          </div>
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

function money(value?: number | null) {
  if (value === null || value === undefined) return "待确认";
  return `$${value.toFixed(2)}`;
}
