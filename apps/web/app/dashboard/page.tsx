"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { Filter } from "lucide-react";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { api, Opportunity, scoreColor } from "@/lib/api";
import { PageTitle, Shell, Stat } from "@/components/Shell";
import { DownloadButton } from "@/components/DownloadButton";

export default function DashboardPage() {
  const [items, setItems] = useState<Opportunity[]>([]);
  const [q, setQ] = useState("");
  const [risk, setRisk] = useState("");

  useEffect(() => {
    api<Opportunity[]>("/opportunities").then(setItems).catch(() => (window.location.href = "/login"));
  }, []);

  const filtered = useMemo(
    () => items.filter((item) => (!q || item.title.toLowerCase().includes(q.toLowerCase())) && (!risk || item.risk_level === risk)),
    [items, q, risk]
  );
  const launchCount = items.filter((item) => item.recommended_action === "上架").length;

  return (
    <Shell>
      <PageTitle title="选品 Dashboard" subtitle="趋势、利润、竞品、库存匹配和风险结果集中查看。" />
      <div className="grid gap-4 md:grid-cols-4">
        <Stat label="候选机会" value={String(items.length)} />
        <Stat label="建议上架" value={String(launchCount)} tone="text-ok" />
        <Stat label="高风险" value={String(items.filter((i) => i.risk_level === "高").length)} tone="text-danger" />
        <Stat label="平均评分" value={items.length ? (items.reduce((a, b) => a + b.opportunity_score, 0) / items.length).toFixed(1) : "0"} />
      </div>
      <section className="mt-5 rounded-md border border-line bg-white p-4">
        <div className="mb-3 flex items-center justify-between">
          <h2 className="text-sm font-semibold">评分分布</h2>
          <DownloadButton path="/exports/opportunities.xlsx" label="导出 Excel" />
        </div>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={items.slice(0, 12)}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="title" tick={{ fontSize: 11 }} />
              <YAxis />
              <Tooltip />
              <Bar dataKey="opportunity_score" fill="#0E7C86" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </section>
      <section className="mt-5 rounded-md border border-line bg-white">
        <div className="flex flex-col gap-3 border-b border-line p-4 md:flex-row md:items-center">
          <div className="relative flex-1">
            <Filter className="absolute left-3 top-2.5 text-slate-400" size={16} />
            <input className="focus-ring w-full rounded-md border border-line py-2 pl-9 pr-3 text-sm" placeholder="筛选关键词、品名" value={q} onChange={(e) => setQ(e.target.value)} />
          </div>
          <select className="focus-ring rounded-md border border-line px-3 py-2 text-sm" value={risk} onChange={(e) => setRisk(e.target.value)}>
            <option value="">全部风险</option>
            <option value="低">低</option>
            <option value="中">中</option>
            <option value="高">高</option>
          </select>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full min-w-[900px] text-left text-sm">
            <thead className="bg-panel text-xs uppercase text-slate-500">
              <tr>
                <th className="px-4 py-3">产品机会</th>
                <th className="px-4 py-3">类目</th>
                <th className="px-4 py-3">机会</th>
                <th className="px-4 py-3">需求</th>
                <th className="px-4 py-3">利润</th>
                <th className="px-4 py-3">匹配</th>
                <th className="px-4 py-3">风险</th>
                <th className="px-4 py-3">动作</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((item) => (
                <tr key={item.id} className="border-t border-line">
                  <td className="px-4 py-3 font-medium"><Link href={`/products/${item.id}`}>{item.title}</Link></td>
                  <td className="px-4 py-3">{item.category}</td>
                  <td className={`px-4 py-3 font-semibold ${scoreColor(item.opportunity_score)}`}>{item.opportunity_score}</td>
                  <td className="px-4 py-3">{item.demand_score}</td>
                  <td className="px-4 py-3">{item.margin_score}</td>
                  <td className="px-4 py-3">{item.catalog_match_score}</td>
                  <td className="px-4 py-3">{item.risk_level}</td>
                  <td className="px-4 py-3">{item.recommended_action}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </Shell>
  );
}
