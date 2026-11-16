export default function StatCard({ title, value, subtitle, icon: Icon, accent = 'indigo' }) {
  const accents = {
    indigo: 'bg-indigo-500/10 text-indigo-400 border-indigo-500/20',
    emerald: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
    amber: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
    rose: 'bg-rose-500/10 text-rose-400 border-rose-500/20',
  };

  return (
    <div className="bg-slate-900/70 border border-slate-800/80 rounded-2xl p-5 hover:border-slate-700/80 transition-all">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs font-medium uppercase tracking-wider text-slate-400">
            {title}
          </p>
          <h3 className="text-2xl font-bold text-white mt-2 font-mono tracking-tight">
            {value}
          </h3>
          {subtitle && (
            <p className="text-xs text-slate-500 mt-1.5">{subtitle}</p>
          )}
        </div>
        <div className={`p-2.5 rounded-xl border ${accents[accent] || accents.indigo}`}>
          <Icon className="w-5 h-5" />
        </div>
      </div>
    </div>
  );
}