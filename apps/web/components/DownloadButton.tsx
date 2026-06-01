"use client";

import { Download } from "lucide-react";
import { API_BASE, token } from "@/lib/api";

export function DownloadButton({ path, label }: { path: string; label: string }) {
  async function download() {
    const response = await fetch(`${API_BASE}${path}`, {
      headers: { Authorization: `Bearer ${token()}` }
    });
    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = label.toLowerCase().includes("excel") ? "opportunities.xlsx" : "opportunities.csv";
    link.click();
    URL.revokeObjectURL(url);
  }

  return (
    <button onClick={download} className="flex items-center gap-2 rounded-md border border-line px-3 py-2 text-sm">
      <Download size={16} />
      {label}
    </button>
  );
}
