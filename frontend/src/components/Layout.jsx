import { NavLink, Outlet, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import {
  Activity,
  LayoutDashboard,
  Layers,
  BellRing,
  LogOut,
  Radio,
} from 'lucide-react';

export default function Layout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate('/login');
  }

  const navItems = [
    { to: '/', icon: LayoutDashboard, label: 'Dashboard' },
    { to: '/applications', icon: Layers, label: 'Aplicações & Keys' },
    { to: '/alerts', icon: BellRing, label: 'Regras de Alerta' },
  ];

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex">
      {/* Sidebar Fixa */}
      <aside className="w-64 bg-slate-900/70 border-r border-slate-800/80 flex flex-col justify-between fixed h-full">
        <div>
          {/* Logo */}
          <div className="h-16 px-6 flex items-center gap-3 border-b border-slate-800/80">
            <div className="w-9 h-9 rounded-lg bg-indigo-600/20 border border-indigo-500/40 flex items-center justify-center text-indigo-400">
              <Activity className="w-5 h-5" />
            </div>
            <div>
              <span className="font-bold tracking-tight text-lg text-white">
                Data<span className="text-indigo-400">Pulse</span>
              </span>
              <p className="text-[10px] uppercase tracking-widest text-slate-500 font-mono">
                Observability
              </p>
            </div>
          </div>

          {/* Links de Navegação */}
          <nav className="p-4 space-y-1.5">
            {navItems.map(({ to, icon: Icon, label }) => (
              <NavLink
                key={to}
                to={to}
                end={to === '/'}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-3.5 py-2.5 rounded-lg text-sm font-medium transition-all ${
                    isActive
                      ? 'bg-indigo-600/15 text-indigo-400 border border-indigo-500/30 shadow-sm'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                  }`
                }
              >
                <Icon className="w-4 h-4" />
                {label}
              </NavLink>
            ))}
          </nav>
        </div>

        {/* Rodapé da Sidebar */}
        <div className="p-4 border-t border-slate-800/80 space-y-3">
          <div className="px-3 py-2 rounded-lg bg-slate-950/60 border border-slate-800/80 flex items-center justify-between">
            <span className="text-xs text-slate-400 flex items-center gap-2">
              <Radio className="w-3.5 h-3.5 text-emerald-400 animate-pulse" />
              Ingestão Ativa
            </span>
            <span className="text-[11px] font-mono text-emerald-400">v1.0</span>
          </div>

          <div className="flex items-center justify-between px-2">
            <div className="truncate pr-2">
              <p className="text-sm font-medium text-slate-200 truncate">
                {user?.full_name || 'Engenheiro'}
              </p>
              <p className="text-xs text-slate-500 truncate">{user?.email}</p>
            </div>
            <button
              onClick={handleLogout}
              title="Sair"
              className="p-2 rounded-lg text-slate-400 hover:text-rose-400 hover:bg-rose-500/10 transition-colors"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        </div>
      </aside>

      {/* Área Principal */}
      <main className="flex-1 ml-64 min-h-screen">
        <div className="max-w-7xl mx-auto p-8">
          <Outlet />
        </div>
      </main>
    </div>
  );
}