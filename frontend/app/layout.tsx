import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
});

export const metadata: Metadata = {
  title: "Weather Proxy",
  description: "A dark editorial weather dashboard powered by Open-Meteo.",
};

const themeBootstrap = `
  (function () {
    try {
      var stored = localStorage.getItem("wp-theme");
      if (stored === "light") {
        document.documentElement.setAttribute("data-theme", "light");
      }
    } catch (e) {}
  })();
`;

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}): React.ReactElement {
  return (
    <html lang="en" className={inter.variable}>
      <head>
        <script dangerouslySetInnerHTML={{ __html: themeBootstrap }} />
      </head>
      <body>{children}</body>
    </html>
  );
}
