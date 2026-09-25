import { Logo } from "../components/Logo";

export default function Loading() {
  return (
    <div className="w-full min-h-[70vh] flex flex-col items-center justify-center gap-4">
      <div className="relative w-14 h-14 flex items-center justify-center">
        <div className="absolute inset-0 rounded-2xl border-2 border-border" />
        <div className="absolute inset-0 rounded-2xl border-2 border-transparent border-t-accent animate-spin-slow" />
        <Logo size={36} />
      </div>
      <p className="text-xs font-semibold text-muted-foreground tracking-wide">
        Loading Verdict…
      </p>
    </div>
  );
}
