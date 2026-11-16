import { useState, useEffect } from 'react';
import api from '../services/api';
import {
  Layers,
  Plus,
  Key,
  Copy,
  Check,
  Trash2,
  Play,
  AlertCircle,
  Sparkles,
} from 'lucide-react';

export default function Applications() {
  const [apps, setApps] = useState([]);
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [createdSecret, setCreatedSecret] = useState(null);
  const [copied, setCopied] = useState(false);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [simulatingId, setSimulatingId] = useState(null);
  const [simFeedback, setSimFeedback] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
    fetchApps();
  }, []);

  async function fetchApps() {
    try {
      const { data } = await api.get('/applications/');
      setApps(data);
    } catch {
      setError('Não foi possível carregar as aplicações.');
    } finally {
      setLoading(false);
    }
  }

  async function handleCreate(e) {
    e.preventDefault();
    setError('');
    setCreating(true);
    setCreatedSecret(null);

    try {
      const { data } = await api.post('/applications/', { name, description });
      setCreatedSecret(data);
      setName('');
      setDescription('');
      fetchApps();
    } catch (err) {
      setError(err.response?.data?.detail || 'Erro ao criar aplicação.');
    } finally {
      setCreating(false);
    }
  }

  async function handleDelete(id) {
    if (!window.confirm('Remover esta aplicação e todas as suas métricas?')) return;
    try {
      await api.delete(`/applications/${id}`);
      setApps((prev) => prev.filter((a) => a.id !== id));
    } catch {
      setError('Erro ao remover aplicação.');
    }
  }

  function copyKey(key) {
    navigator.clipboard.writeText(key);
    setCopied(true);
    setTimeout(() => setCopied(false), 2500);
  }

  async function handleSimulateTraffic(app) {
    const apiKey = app.api_key || createdSecret?.api_key;
    if (!apiKey) {
      setSimFeedback('Informe ou use uma aplicação cuja API Key esteja visível.');
      return;
    }

    setSimulatingId(app.id);
    setSimFeedback('');

    const sampleEndpoints = [
      { endpoint: '/api/v1/checkout', method: 'POST', status: 200, minMs: 120, maxMs: 480 },
      { endpoint: '/api/v1/users/profile', method: 'GET', status: 200, minMs: 18, maxMs: 75 },
      { endpoint: '/api/v1/reports/export', method: 'GET', status: 200, minMs: 650, maxMs: 1450 },
      { endpoint: '/api/v1/payments/webhook', method: 'POST', status: 500, minMs: 300, maxMs: 900 },
      { endpoint: '/api/v1/products', method: 'GET', status: 200, minMs: 25, maxMs: 110 },
    ];

    try {
      for (let i = 0; i < 10; i++) {
        const sample = sampleEndpoints[Math.floor(Math.random() * sampleEndpoints.length)];
        const responseTime = Math.floor(
          Math.random() * (sample.maxMs - sample.minMs + 1) + sample.minMs
        );

        await api.post(
          '/ingest/',
          {
            endpoint: sample.endpoint,
            method: sample.method,
            status_code: sample.status,
            response_time_ms: responseTime,
          },
          {
            headers: { 'X-API-Key': apiKey },
          }
        );
      }
      setSimFeedback(`10 eventos enviados para "${app.name}"! Confira os gráficos no Dashboard.`);
    } catch {
      setSimFeedback('Falha ao simular tráfego. Verifique se a chave da aplicação é válida.');
    } finally {
      setSimulatingId(null);
    }
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight">
          Aplicações & Chaves de Ingestão
        </h1>
        <p className="text-sm text-slate-400 mt-1">
          Gerencie os serviços monitorados e suas credenciais <code className="text-indigo-400 font-mono">X-API-Key</code>
        </p>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 flex items-center gap-2.5 text-sm text-rose-300">
          <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {simFeedback && (
        <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/30 flex items-center gap-2.5 text-sm text-emerald-300">
          <Sparkles className="w-4 h-4 text-emerald-400 shrink-0" />
          <span>{simFeedback}</span>
        </div>
      )}

      {/* Banner da Nova API Key Gerada */}
      {createdSecret?.api_key && (
        <div className="bg-indigo-950/50 border border-indigo-500/40 rounded-2xl p-6 space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-indigo-300 flex items-center gap-2">
              <Key className="w-4 h-4" />
              Chave de Ingestão Gerada ({createdSecret.name})
            </span>
            <span className="text-xs text-amber-300">
              Guarde esta chave agora — ela pode não ser exibida novamente
            </span>
          </div>
          <div className="flex items-center gap-3 bg-slate-950 border border-slate-800 rounded-xl p-3">
            <code className="text-sm font-mono text-emerald-400 flex-1 truncate">
              {createdSecret.api_key}
            </code>
            <button
              onClick={() => copyKey(createdSecret.api_key)}
              className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-medium text-white flex items-center gap-1.5 transition-colors"
            >
              {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
              {copied ? 'Copiada!' : 'Copiar'}
            </button>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Formulário de Nova Aplicação */}
        <form
          onSubmit={handleCreate}
          className="bg-slate-900/70 border border-slate-800/80 rounded-2xl p-6 space-y-4 h-fit"
        >
          <h2 className="text-base font-semibold text-white flex items-center gap-2">
            <Plus className="w-4 h-4 text-indigo-400" />
            Nova Aplicação
          </h2>

          <div>
            <label className="block text-xs font-medium text-slate-400 mb-1.5">
              Nome do Serviço
            </label>
            <input
              type="text"
              required
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Ex: Payment Gateway API"
              className="w-full bg-slate-950/80 border border-slate-800 rounded-xl px-3.5 py-2.5 text-sm text-slate-100 placeholder-slate-600 focus:outline-none focus:border-indigo-500"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-400 mb-1.5">
              Descrição (opcional)
            </label>
            <textarea
              rows={3}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Microsserviço responsável pelo processamento de checkout..."
              className="w-full bg-slate-950/80 border border-slate-800 rounded-xl px-3.5 py-2.5 text-sm text-slate-100 placeholder-slate-600 focus:outline-none focus:border-indigo-500 resize-none"
            />
          </div>

          <button
            type="submit"
            disabled={creating}
            className="w-full bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white text-sm font-medium py-2.5 rounded-xl transition-all shadow-lg shadow-indigo-600/20"
          >
            {creating ? 'Gerando API Key...' : 'Registrar Aplicação'}
          </button>
        </form>

        {/* Lista de Aplicações */}
        <div className="lg:col-span-2 space-y-4">
          {loading ? (
            <p className="text-sm text-slate-400">Carregando serviços...</p>
          ) : apps.length === 0 ? (
            <div className="bg-slate-900/40 border border-dashed border-slate-800 rounded-2xl p-10 text-center">
              <Layers className="w-8 h-8 text-slate-600 mx-auto mb-2" />
              <p className="text-sm text-slate-400">
                Nenhuma aplicação cadastrada ainda. Use o formulário ao lado para começar.
              </p>
            </div>
          ) : (
            apps.map((app) => {
              const hasVisibleKey = Boolean(app.api_key || (createdSecret?.id === app.id && createdSecret?.api_key));
              return (
                <div
                  key={app.id}
                  className="bg-slate-900/70 border border-slate-800/80 rounded-2xl p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4"
                >
                  <div className="space-y-1">
                    <div className="flex items-center gap-2.5">
                      <h3 className="font-semibold text-white">{app.name}</h3>
                      <span className="text-[11px] font-mono px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                        ID #{app.id}
                      </span>
                    </div>
                    <p className="text-xs text-slate-400">
                      {app.description || 'Sem descrição informada'}
                    </p>
                    {app.api_key && (
                      <p className="text-xs font-mono text-slate-500 pt-1">
                        Key: <span className="text-slate-300">{app.api_key}</span>
                      </p>
                    )}
                  </div>

                  <div className="flex items-center gap-2 shrink-0">
                    {hasVisibleKey && (
                      <button
                        onClick={() => handleSimulateTraffic(app)}
                        disabled={simulatingId === app.id}
                        className="px-3 py-2 rounded-xl bg-emerald-500/10 hover:bg-emerald-500/20 border border-emerald-500/30 text-emerald-300 text-xs font-medium flex items-center gap-1.5 transition-colors"
                        title="Enviar 10 métricas de exemplo"
                      >
                        <Play className="w-3.5 h-3.5" />
                        {simulatingId === app.id ? 'Enviando...' : 'Simular Tráfego'}
                      </button>
                    )}

                    <button
                      onClick={() => handleDelete(app.id)}
                      className="p-2 rounded-xl text-slate-400 hover:text-rose-400 hover:bg-rose-500/10 transition-colors"
                      title="Excluir aplicação"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              );
            })
          )}
        </div>
      </div>
    </div>
  );
}