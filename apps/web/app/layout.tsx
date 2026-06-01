import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "WestMonth Amazon US 选品云",
  description: "内部 Amazon US 选品、趋势、利润、风险与库存匹配平台"
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="zh-CN">
      <body>{children}</body>
    </html>
  );
}
