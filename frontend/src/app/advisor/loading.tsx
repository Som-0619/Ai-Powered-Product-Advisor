import { Sparkles } from "lucide-react";

export default function AdvisorLoading() {
  return (
    <div className="w-full max-w-5xl mx-auto py-10 space-y-6 animate-pulse">
      <div className="flex justify-center">
        <div className="h-9 w-64 rounded-xl bg-surface-100 border border-border" />
      </div>
      <div className="max-w-2xl mx-auto text-center space-y-3">
        <div className="h-8 w-72 mx-auto rounded-lg bg-surface-100" />
        <div className="h-4 w-96 max-w-full mx-auto rounded-lg bg-surface-100" />
        <div className="h-12 w-full rounded-xl bg-surface-100 border border-border mt-4 flex items-center justify-center gap-2">
          <Sparkles className="w-4 h-4 text-muted-foreground/40" />
        </div>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-5xl mx-auto">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="h-32 rounded-xl bg-surface-100 border border-border" />
        ))}
      </div>
    </div>
  );
}
