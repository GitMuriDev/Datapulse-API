import { useState, useEffect } from 'react';
import api from '../services/api';
import { BellRing, Plus, Trash2, ShieldAlert, CheckCircle2 } from 'lucide-react';

export default function Alerts() {
  const [apps, setApps] = useState([]);
  const [selectedAppId, setSelectedAppId] = useState('');
  const [rules, setRules] = useState([]);
  const [metricType, setMetricType] = useState('response_time_ms');
  const [threshold, setThreshold] = useState('500');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    init();
  }, []);

  useEffect(() => {
    if (selectedAppId) {
      fetchRules(selectedAppId);
    }
  }, [selectedAppId]);

  async function init() {
    try {
      const { data } = await api.get('/applications/');
      setApps(data);
      if (data.length > 0) {
        setSelectedAppId(String(data[0].id));
      }
    } finally {
      setLoading(false);
    }
  }

  async function fetchRules(appId) {
    try {
      const { data } = await api.get(`/alerts/rules/${appId}`);
      setRules(Array.isArray(data) ? data : []);
    } catch {
      setRules([]);
    }
  }

  async function handleCreateRule(e) {
    e.preventDefault();
    if (!selectedAppId) return;
    setSaving(true);

    try {
      await api.post('/alerts/rules', {
        application_id: Number(selectedAppId),
        metric_type: metricType,
        threshold: Number(threshold),
        is_active: true,
      });
      fetchRules(selectedAppId);
    } finally {
      setSaving(false);
    }
  }

  async function handleDeleteRule(ruleId) {
    try {
      await api.delete(`/alerts/rules/${ruleId}`);
      setRules((prev) => prev.filter((r) => r.id !== ruleId));
    } catch (err) {
      console.error(err);
    }
  }

  if (loading) {
    return <p className="text-sm text-slate-400">Carregando regras de alerta...</p>;
  }

  return (
    <div className="space-y-8">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">
            Regras de Alerta & Thresholds
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Defina limites críticos de latência ou códigos de erro para disparo automático de incidentes
          </p>
        </div>

        {apps.length > 0 && (
          <select
            value={selectedAppId}
            onChange={(e) => setSelectedAppId(e.target.value)}
            className="bg-slate-900 border border-slate-700/80 rounded-xl px-4 py-2 text-sm text-slate-100 focus:outline-none focus:border-indigo-500"
          >
            {apps.map((app) => (
              <option key={app.id} value={app.id}>
                {app.name}
              </option>
            ))}
          </select>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <form
          onSubmit={handleCreateRule}
          className="bg-slate-900/70 border border-slate-800/80 rounded-2xl p-6 space-y-4 h-fit"
        >
          <h2 className="text-base font-semibold text-white flex items-center gap-2">
            <Plus className="w-4 h-4 text-indigo-400" />
            Nova Regra de Monitoramento
          </h2>

          <div>
            <label className="block text-xs font-medium text-slate-400 mb-1.5">
              Métrica Monitorada
            </label>
            <select
              value={metricType}
              onChange={(e) => setMetricType(e.target.value)}
              className="w-full bg-slate-950/80 border border-slate-800 rounded-xl px-3.5 py-2.5 text-sm text-slate-100 focus:outline-none focus:border-indigo-500"
            >
              <option value="response_time_ms">Latência (response_time_ms)</option>
              <option value="status_code">Código HTTP (status_code &gt;=)</option>
            </select>
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-400 mb-1.5">
              Limite Crítico (Threshold)
            </label>
            <input
              type="number"
              required
              value={threshold}
              onChange={(e) => setThreshold(e.target.value)}
              placeholder="Ex: 500"
              className="w-full bg-slate-950/80 border border-slate-800 rounded-xl px-3.5 py-2.5 text-sm font-mono text-slate-100 focus:outline-none focus:border-indigo-500"
            />
            <p className="text-[11px] text-slate-500 mt-1">
              {metricType === 'response_time_ms'
                ? 'Dispara alerta quando a requisição ultrapassar este valor em ms.'
                : 'Dispara alerta quando o status HTTP for igual ou superior (ex: 500).'}
            </p>
          </div>

          <button
            type="submit"
            disabled={saving || !selectedAppId}
            className="w-full bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white text-sm font-medium py-2.5 rounded-xl transition-all"
          >
            {saving ? 'Salvando...' : 'Ativar Regra'}
          </button>
        </form>

        <div className="lg:col-span-2 space-y-4">
          {rules.length === 0 ? (
            <div className="bg-slate-900/40 border border-dashed border-slate-800 rounded-2xl p-10 text-center">
              <BellRing className="w-8 h-8 text-slate-600 mx-auto mb-2" />
              <p className="text-sm text-slate-400">
                Nenhuma regra configurada para esta aplicação.
              </p>
            </div>
          ) : (
            rules.map((rule) => (
              <div
                key={rule.id}
                className="bg-slate-900/70 border border-slate-800/80 rounded-2xl p-5 flex items-center justify-between"
              >
                <div className="flex items-center gap-4">
                  <div className="p-2.5 rounded-xl bg-amber-500/10 border border-amber-500/20 text-amber-400">
                    <ShieldAlert className="w-5 h-5" />
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-sm font-semibold text-white">
                        {rule.metric_type}
                      </span>
                      <span className="text-xs px-2 py-0.5 rounded bg-slate-800 text-amber-300 font-mono">
                        &gt; {rule.threshold}
                      </span>
                    </div>
                    <p className="text-xs text-emerald-400 flex items-center gap-1 mt-1">
                      <CheckCircle2 className="w-3.5 h-3.5" />
                      Monitoramento ativo
                    </p>
                  </div>
                </div>

                <button
                  onClick={() => handleDeleteRule(rule.id)}
                  className="p-2 rounded-xl text-slate-400 hover:text-rose-400 hover:bg-rose-500/10 transition-colors"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}