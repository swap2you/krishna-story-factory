import type { ReactNode } from "react";
import { VaniPlayerProvider } from "@/components/vani/vani-player";

export default function PrabhupadaVaniLayout({ children }: { children: ReactNode }) {
  return <VaniPlayerProvider>{children}</VaniPlayerProvider>;
}
