import { Cpu } from "lucide-react";

export default function Loading() {
  return (
    <div className="w-full min-h-[70vh] flex flex-col items-center justify-center gap-4">
      <div className="relative w-14 h-14 flex items-center justify-center">
        <div className="absolute inset-0 rounded-2xl border-2 border-border" />
        <div className="absolute inset-0 rounded-2xl border-2 border-transparent border-t-blue-600 animate-spin-slow" />
        <div className="w-9 h-9 rounded-xl bg-blue-600 flex items-center justify-center shadow-sm">
          <Cpu className="w-5 h-5 text-white" />
        </div>
      </div>
      <p className="text-xs font-semibold text-muted-foreground tracking-wide">
        Loading Product Advisor…
      </p>
    </div>
  );
}
