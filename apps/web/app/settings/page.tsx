"use client";

import { useEffect, useState } from "react";
import { Database, RefreshCw } from "lucide-react";
import { api } from "@/lib/api";
import { PageTitle, Shell } from "@/components/Shell";
import { DownloadButton } from "@/components/DownloadButton";

type Job = { id: number; job_type: string; status: string; created_at: string; message: string | null };

export default function SettingsPage() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const refresh = () => api<Job[]>("/jobs").then(setJobs);
  useEffect(() => { refresh(); }, []);
  return (
    <Shell>
      <PageTitle title="设置 / 同步任务" subtitle="管理数据同步、货盘导入、导出和后续数据源扩展。" />
      <div className="grid gap-4 lg:grid-cols-2">
        <section className="rounded-md border border-line bg-white p-4">
          <h2 className="flex items-center gap-2 text-sm font-semibold"><RefreshCw size={16} /> 定时同步</h2>
          <div className="mt-4 grid gap-3 sm:grid-cols-2">
            {["westmonth_catalog_refresh", "amazon_keyword_recheck", "trend_snapshot"].map((job) => (
              <button key={job} onClick={() => api(`/jobs/schedule?job_type=${job}`, { method: "POST" }).then(refresh)} className="rounded-md border border-line px-3 py-2 text-sm hover:border-brand">
                {job}
              </button>
            ))}
          </div>
        </section>
        <section className="rounded-md border border-line bg-white p-4">
          <h2 className="flex items-center gap-2 text-sm font-semibold"><Database size={16} /> 导出</h2>
          <div className="mt-4 flex gap-3">
            <DownloadButton path="/exports/opportunities.csv" label="CSV" />
            <DownloadButton path="/exports/opportunities.xlsx" label="Excel" />
          </div>
        </section>
      </div>
      <section className="mt-5 rounded-md border border-line bg-white">
        <div className="border-b border-line p-4 text-sm font-semibold">任务日志</div>
        <div className="divide-y divide-line">
          {jobs.map((job) => (
            <div key={job.id} className="grid grid-cols-[80px_1fr_120px] gap-3 px-4 py-3 text-sm">
              <span>{job.id}</span>
              <span>{job.job_type}</span>
              <span>{job.status}</span>
            </div>
          ))}
        </div>
      </section>
    </Shell>
  );
}
