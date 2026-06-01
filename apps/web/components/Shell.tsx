"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { BarChart3, BookmarkCheck, Gauge, LogOut, Search, Settings, ShieldAlert, TrendingUp } from "lucide-react";

const nav = [
  { href: "/dashboard", label: "Dashboard", icon: Gauge },
  { href: "/search", label: "搜索", icon: Search },
  { href: "/risk", label: "风险", icon: ShieldAlert },
  { href: "/trends", label: "趋势", icon: TrendingUp },
  { href: "/settings", label: "设置", icon: Settings }
];

export function Shell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  return (
    <div className="min-h-screen bg-[#F2F5F8]">
      <aside className="fixed inset-y-0 left-0 hidden w-64 border-r border-line bg-white px-4 py-5 lg:block">
        <div className="mb-8 flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-md bg-brand text-white">
            <BookmarkCheck size={20} />
          </div>
          <div>
            <div className="text-sm font-semibold">WestMonth</div>
            <div className="text-xs text-slate-500">Amazon US 选品云</div>
          </div>
        </div>
        <nav className="space-y-1">
          {nav.map((item) => {
            const Icon = item.icon;
            const active = pathname.startsWith(item.href);
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center gap-3 rounded-md px-3 py-2 text-sm ${
                  active ? "bg-brand text-white" : "text-slate-700 hover:bg-panel"
                }`}
              >
                <Icon size={17} />
                {item.label}
              </Link>
            );
          })}
        </nav>
        <button
          className="absolute bottom-5 left-4 right-4 flex items-center justify-center gap-2 rounded-md border border-line px-3 py-2 text-sm"
          onClick={() => {
            localStorage.removeItem("wm_token");
            window.location.href = "/login";
          }}
        >
          <LogOut size={16} />
          退出
        </button>
      </aside>
      <main className="lg:pl-64">
        <div className="mx-auto max-w-7xl px-4 py-5 sm:px-6 lg:px-8">{children}</div>
      </main>
    </div>
  );
}

export function Stat({ label, value, tone }: { label: string; value: string; tone?: string }) {
  return (
    <div className="rounded-md border border-line bg-white p-4">
      <div className="text-xs text-slate-500">{label}</div>
      <div className={`mt-2 text-2xl font-semibold ${tone ?? "text-ink"}`}>{value}</div>
    </div>
  );
}

export function PageTitle({ title, subtitle }: { title: string; subtitle: string }) {
  return (
    <div className="mb-5">
      <h1 className="text-2xl font-semibold tracking-normal text-ink">{title}</h1>
      <p className="mt-1 text-sm text-slate-600">{subtitle}</p>
    </div>
  );
}
