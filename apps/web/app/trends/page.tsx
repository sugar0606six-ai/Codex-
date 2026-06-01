"use client";

import { useEffect, useState } from "react";
import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { api, Opportunity } from "@/lib/api";
import { PageTitle, Shell } from "@/components/Shell";

export default function TrendsPage() {
  const [items, setItems] = useState<Opportunity[]>([]);
  useEffect(() => { api<Opportunity[]>("/opportunities").then(setItems); }, []);
  const data = items.map((item) => ({ name: item.title, demand: item.demand_score, score: item.opportunity_score }));
  return (
    <Shell>
      <PageTitle title="趋势看板" subtitle="展示候选词需求趋势和机会评分，后续可接入 Google Trends、TikTok、Reddit 实时数据。" />
      <section className="rounded-md border border-line bg-white p-4">
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data}>
              <XAxis dataKey="name" tick={{ fontSize: 11 }} />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="demand" stroke="#0E7C86" strokeWidth={2} />
              <Line type="monotone" dataKey="score" stroke="#E36B2C" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </section>
    </Shell>
  );
}
