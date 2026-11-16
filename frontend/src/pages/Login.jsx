import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Activity, Lock, Mail, User, ArrowRight, AlertCircle } from 'lucide-react';

export default function Login() {
  const [isRegister, setIsRegister] = useState(false);
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const { login, register } = useAuth();
  const navigate = useNavigate();

  async function handleSubmit(e) {
    e.preventDefault();
    setError('');
    setSubmitting(true);

    try {
      if (isRegister) {
        await register(fullName, email, password);
      } else {
        await login(email, password);
      }
      navigate('/');
    } catch (err) {
      const detail = err.response?.data?.detail;
      setError(
        typeof detail === 'string'
          ? detail
          : 'Não foi possível autenticar. Verifique suas credenciais.'
      );
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="min-h-screen bg-slate-950 flex items-center justify-center p-4 relative overflow-hidden">
      {/* Brilho de fundo sutil */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-[500px] h-[500px] bg-indigo-600/10 rounded-full blur-3xl pointer-events-none" />

      <div className="w-full max-w-md bg-slate-900/80 backdrop-blur-xl border border-slate-800 rounded-2xl p-8 shadow-2xl relative z-10">
        {/* Cabeçalho */}
        <div className="flex flex-col items-center text-center mb-8">
          <div className="w-12 h-12 rounded-xl bg-indigo-600/20 border border-indigo-500/40 flex items-center justify-center text-indigo-400 mb-4">
            <Activity className="w-6 h-6" />
          </div>
          <h1 className="text-2xl font-bold text-white tracking-tight">
            Data<span className="text-indigo-400">Pulse</span>
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            {isRegister
              ? 'Crie sua conta para monitorar suas APIs em tempo real'
              : 'Acesse seu painel de telemetria e observabilidade'}
          </p>
        </div>

        {error && (
          <div className="mb-5 p-3.5 rounded-xl bg-rose-500/10 border border-rose-500/30 flex items-center gap-2.5 text-sm text-rose-300">
            <AlertCircle className="w-4 h-4 shrink-0 text-rose-400" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          {isRegister && (
            <div>
              <label className="block text-xs font-medium text-slate-400 mb-1.5">
                Nome Completo
              </label>
              <div className="relative">
                <User className="w-4 h-4 text-slate-500 absolute left-3.5 top-1/2 -translate-y-1/2" />
                <input
                  type="text"
                  required
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  placeholder="Ex: Murilo Filho"
                  className="w-full bg-slate-950/80 border border-slate-800 rounded-xl pl-10 pr-4 py-2.5 text-sm text-slate-100 placeholder-slate-600 focus:outline-none focus:border-indigo-500 transition-colors"
                />
              </div>
            </div>
          )}

          <div>
            <label className="block text-xs font-medium text-slate-400 mb-1.5">
              E-mail Corporativo ou Pessoal
            </label>
            <div className="relative">
              <Mail className="w-4 h-4 text-slate-500 absolute left-3.5 top-1/2 -translate-y-1/2" />
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="voce@exemplo.com"
                className="w-full bg-slate-950/80 border border-slate-800 rounded-xl pl-10 pr-4 py-2.5 text-sm text-slate-100 placeholder-slate-600 focus:outline-none focus:border-indigo-500 transition-colors"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-400 mb-1.5">
              Senha
            </label>
            <div className="relative">
              <Lock className="w-4 h-4 text-slate-500 absolute left-3.5 top-1/2 -translate-y-1/2" />
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full bg-slate-950/80 border border-slate-800 rounded-xl pl-10 pr-4 py-2.5 text-sm text-slate-100 placeholder-slate-600 focus:outline-none focus:border-indigo-500 transition-colors"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={submitting}
            className="w-full mt-2 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white font-medium py-2.5 rounded-xl flex items-center justify-center gap-2 transition-all shadow-lg shadow-indigo-600/20"
          >
            {submitting
              ? 'Processando...'
              : isRegister
              ? 'Criar Conta e Entrar'
              : 'Entrar no Painel'}
            {!submitting && <ArrowRight className="w-4 h-4" />}
          </button>
        </form>

        <div className="mt-6 pt-5 border-t border-slate-800/80 text-center">
          <button
            type="button"
            onClick={() => {
              setIsRegister(!isRegister);
              setError('');
            }}
            className="text-xs text-slate-400 hover:text-indigo-400 transition-colors"
          >
            {isRegister
              ? 'Já possui uma conta? Faça login'
              : 'Ainda não tem conta? Cadastre-se agora'}
          </button>
        </div>
      </div>
    </div>
  );
}