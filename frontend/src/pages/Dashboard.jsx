import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../services/api';
import StatCard from '../components/StatCard';
import {
  Activity,
  Clock,
  AlertTriangle,
  CheckCircle2,
  RefreshCw,
  Plus,
  Server,
  Zap,
} from 'lucide-react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Cell,
} from 'recharts';

export default function Dashboard() {
  const [apps, setApps] = useState([]);
  const [selectedAppId, setSelectedAppId] = useState('');
  const [summary, setSummary] = useState(null);
  const [slowest, setSlowest] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadApplications();
  }, []);

  useEffect(() => {
    if (selectedAppId) {
      loadMetrics(selectedAppId);
    }
  }, [selectedAppId]);

  async function loadApplications() {
    try {
      const { data } = await api.get('/applications/');
      setApps(data);
      if (data.length > 0) {
        setSelectedAppId(String(data[0].id));
      }
    } catch (err) {
      console.error('Erro ao carregar aplicações:', err);
    } finally {
      setLoading(false);
    }
  }

  async function loadMetrics(appId) {
    setRefreshing(true);
    try {
      const [summaryRes, slowestRes] = await Promise.all([
        api.get(`/metrics/summary/${appId}`).catch(() => ({ data: null })),
        api.get(`/metrics/slowest/${appId}`).catch(() => ({ data: [] })),
      ]);
      setSummary(summaryRes.data);
      setSlowest(Array.isArray(slowestRes.data) ? slowestRes.data : []);
    } finally {
      setRefreshing(false);
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96 text-slate-400 gap-3">
        <RefreshCw className="w-5 h-5 animate-spin text-indigo-400" />
        <span>Carregando telemetria...</span>
      </div>
    );
  }

  if (apps.length === 0) {
    return (
      <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-12 text-center max-w-xl mx-auto mt-12">
        <div className="w-14 h-14 rounded-2xl bg-indigo-500/10 border border-indigo-500/30 flex items-center justify-center text-indigo-400 mx-auto mb-4">
          <Server className="w-7 h-7" />
        </div>
        <h2 className="text-xl font-bold text-white">Nenhuma aplicação monitorada</h2>
        <p className="text-sm text-slate-400 mt-2 mb-6">
          Cadastre sua primeira API para gerar uma chave de ingestão e começar a visualizar métricas em tempo real.
        </p>
        <Link
          to="/applications"
          className="inline-flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-medium px-5 py-2.5 rounded-xl transition-all"
        >
          <Plus className="w-4 h-4" />
          Criar Primeira Aplicação
        </Link>
      </div>
    );
  }

  const totalRequests = summary?.total_requests ?? 0;
  const avgLatency = summary?.avg_response_time_ms
    ? `${Number(summary.avg_response_time_ms).toFixed(1)} ms`
    : '0.0 ms';
  const errorRate = summary?.error_rate != null
    ? `${Number(summary.error_rate).toFixed(2)}%`
    : '0.00%';
  const successCount = summary?.success_count ?? Math.max(0, totalRequests - (summary?.error_count ?? 0));
  const errorCount = summary?.error_count ?? 0;

  const statusChartData = [
    { name: 'Sucesso (2xx/3xx)', total: successCount, color: '#10b981' },
    { name: 'Erros (4xx/5xx)', total: errorCount, color: '#f43f5e' },
  ];

  return (
    <div className="space-y-8">
      {/* Cabeçalho + Seletor de Aplicação */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">
            Visão Geral de Telemetria
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Latência, volume de tráfego e saúde dos endpoints monitorados
          </p>
        </div>

        <div className="flex items-center gap-3">
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

          <button
            onClick={() => loadMetrics(selectedAppId)}
            disabled={refreshing}
            className="p-2.5 rounded-xl bg-slate-900 border border-slate-800 hover:border-slate-700 text-slate-300 hover:text-white transition-all"
            title="Atualizar métricas"
          >
            <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin text-indigo-400' : ''}`} />
          </button>
        </div>
      </div>

      {/* Grid de KPIs */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <StatCard
          title="Total de Requisições"
          value={totalRequests.toLocaleString('pt-BR')}
          subtitle="Eventos ingeridos no período"
          icon={Activity}
          accent="indigo"
        />
        <StatCard
          title="Latência Média"
          value={avgLatency}
          subtitle="Tempo médio de resposta"
          icon={Clock}
          accent="amber"
        />
        <StatCard
          title="Taxa de Erro"
          value={errorRate}
          subtitle={`${errorCount} falhas registradas`}
          icon={AlertTriangle}
          accent={Number(summary?.error_rate ?? 0) > 5 ? 'rose' : 'emerald'}
        />
        <StatCard
          title="Disponibilidade"
          value={totalRequests > 0 ? `${(100 - Number(summary?.error_rate ?? 0)).toFixed(2)}%` : '100%'}
          subtitle="SLA calculado sobre requisições"
          icon={CheckCircle2}
          accent="emerald"
        />
      </div>

      {/* Gráficos e Tabela */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Gráfico de Distribuição de Respostas */}
        <div className="bg-slate-900/70 border border-slate-800/80 rounded-2xl p-6">
          <h2 className="text-base font-semibold text-white mb-1">
            Distribuição de Respostas
          </h2>
          <p className="text-xs text-slate-400 mb-6">
            Proporção entre requisições saudáveis e erros
          </p>

          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={statusChartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                <XAxis dataKey="name" tick={{ fill: '#94a3b8', fontSize: 12 }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fill: '#94a3b8', fontSize: 12 }} axisLine={false} tickLine={false} />
                <Tooltip
                  cursor={{ fill: '#0f172a' }}
                  contentStyle={{
                    backgroundColor: '#0f172a',
                    borderColor: '#1e293b',
                    borderRadius: '12px',
                    color: '#f8fafc',
                  }}
                />
                <Bar dataKey="total" radius={[8, 8, 0, 0]} barSize={48}>
                  {statusChartData.map((entry, idx) => (
                    <Cell key={idx} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Endpoints Mais Lentos */}
        <div className="lg:col-span-2 bg-slate-900/70 border border-slate-800/80 rounded-2xl p-6">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-base font-semibold text-white flex items-center gap-2">
                <Zap className="w-4 h-4 text-amber-400" />
                Gargalos & Endpoints Mais Lentos
              </h2>
              <p className="text-xs text-slate-400 mt-0.5">
                Rotas ordenadas pelo maior tempo médio de resposta
              </p>
            </div>
          </div>

          {slowest.length === 0 ? (
            <div className="h-56 flex flex-col items-center justify-center text-center border border-dashed border-slate-800 rounded-xl p-6">
              <p className="text-sm text-slate-400">
                Nenhuma métrica de endpoint registrada para esta aplicação ainda.
              </p>
              <p className="text-xs text-slate-500 mt-1">
                Vá em <span className="text-indigo-400">Aplicações & Keys</span> para enviar um evento de teste via API Key.
              </p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="border-b border-slate-800 text-[11px] uppercase tracking-wider text-slate-400">
                    <th className="pb-3 font-medium">Método</th>
                    <th className="pb-3 font-medium">Endpoint</th>
                    <th className="pb-3 font-medium text-right">Chamadas</th>
                    <th className="pb-3 font-medium text-right">Latência Média</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60 text-sm">
                  {slowest.map((item, idx) => (
                    <tr key={idx} className="hover:bg-slate-800/30 transition-colors">
                      <td className="py-3.5">
                        <span className="px-2 py-0.5 rounded text-xs font-mono font-semibold bg-indigo-500/15 text-indigo-400 border border-indigo-500/30">
                          {item.method || 'GET'}
                        </span>
                      </td>
                      <td className="py-3.5 font-mono text-xs text-slate-200">
                        {item.endpoint}
                      </td>
                      <td className="py-3.5 text-right text-slate-400 font-mono">
                        {item.request_count ?? item.count ?? '-'}
                      </td>
                      <td className="py-3.5 text-right font-mono font-semibold text-amber-400">
                        {Number(item.avg_response_time_ms).toFixed(1)} ms
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}