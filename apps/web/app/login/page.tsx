"use client";

import { useState } from "react";
import { api } from "@/lib/api";

export default function LoginPage() {
  const [email, setEmail] = useState("admin@westmonth.local");
  const [password, setPassword] = useState("ChangeMe123!");
  const [error, setError] = useState("");

  async function submit(event: React.FormEvent) {
    event.preventDefault();
    setError("");
    try {
      const data = await api<{ access_token: string }>("/auth/login", {
        method: "POST",
        body: JSON.stringify({ email, password })
      });
      localStorage.setItem("wm_token", data.access_token);
      window.location.href = "/dashboard";
    } catch {
      setError("登录失败，请确认账号、密码和后端服务状态。");
    }
  }

  return (
    <main className="grid min-h-screen place-items-center bg-[#F2F5F8] px-4">
      <form onSubmit={submit} className="w-full max-w-sm rounded-md border border-line bg-white p-6 shadow-sm">
        <h1 className="text-xl font-semibold">WestMonth 选品云</h1>
        <p className="mt-1 text-sm text-slate-600">内部账号登录</p>
        <label className="mt-6 block text-sm font-medium">邮箱</label>
        <input className="focus-ring mt-2 w-full rounded-md border border-line px-3 py-2" value={email} onChange={(e) => setEmail(e.target.value)} />
        <label className="mt-4 block text-sm font-medium">密码</label>
        <input className="focus-ring mt-2 w-full rounded-md border border-line px-3 py-2" type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
        {error ? <div className="mt-4 rounded-md bg-red-50 px-3 py-2 text-sm text-danger">{error}</div> : null}
        <button className="focus-ring mt-6 w-full rounded-md bg-brand px-4 py-2 text-sm font-semibold text-white">登录</button>
      </form>
    </main>
  );
}
