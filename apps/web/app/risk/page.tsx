"use client";

import { useEffect, useState } from "react";
import { AlertTriangle, ShieldCheck } from "lucide-react";
import { api } from "@/lib/api";
import { PageTitle, Shell } from "@/components/Shell";

type Risk = {
  id: number;
  keyword_id: number;
  infringement_risk: string;
  patent_risk: string;
  trademark_risk: string;
  compliance_risk: string;
  risk_score: number;
  review_required: boolean;
  rationale: string;
};

export default function RiskPage() {
  const [items, setItems] = useState<Risk[]>([]);
  useEffect(() => { api<Risk[]>("/risk").then(setItems); }, []);
  return (
    <Shell>
      <PageTitle title="风险 / 侵权审查" subtitle="高风险默认标红，不进入自动上架建议。" />
      <section className="rounded-md border border-line bg-white">
        <div className="overflow-x-auto">
          <table className="w-full min-w-[850px] text-left text-sm">
            <thead className="bg-panel text-xs uppercase text-slate-500">
              <tr>
                <th className="px-4 py-3">Keyword ID</th>
                <th className="px-4 py-3">风险分</th>
                <th className="px-4 py-3">侵权</th>
                <th className="px-4 py-3">专利</th>
                <th className="px-4 py-3">商标</th>
                <th className="px-4 py-3">合规</th>
                <th className="px-4 py-3">复核</th>
              </tr>
            </thead>
            <tbody>
              {items.map((item) => (
                <tr key={item.id} className="border-t border-line">
                  <td className="px-4 py-3">{item.keyword_id}</td>
                  <td className={`px-4 py-3 font-semibold ${item.risk_score >= 70 ? "text-danger" : "text-slate-800"}`}>{item.risk_score}</td>
                  <td className="px-4 py-3">{item.infringement_risk}</td>
                  <td className="px-4 py-3">{item.patent_risk}</td>
                  <td className="px-4 py-3">{item.trademark_risk}</td>
                  <td className="px-4 py-3">{item.compliance_risk}</td>
                  <td className="px-4 py-3">{item.review_required ? <AlertTriangle className="text-danger" size={17} /> : <ShieldCheck className="text-ok" size={17} />}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </Shell>
  );
}
