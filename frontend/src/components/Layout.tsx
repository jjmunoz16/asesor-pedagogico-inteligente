import { useEffect, useState } from 'react';
import { Link, NavLink, Outlet } from 'react-router-dom';
import {
  BookOpen,
  ClipboardCheck,
  Cpu,
  FolderGit2,
  GraduationCap,
  KeyRound,
  LineChart,
  LogIn,
  LogOut,
  Network,
  ShieldCheck,
  Sparkles,
} from 'lucide-react';
import { apiRequest } from '../api/client';
import { useAuth } from '../auth/AuthContext';
import type { UserRole } from '../types';

export function Layout() {
  const { user, token, isOpenDemo, demoRole, switchDemoRole, logout } = useAuth();
  const [apiStatus, setApiStatus] = useState<'checking' | 'online' | 'waking'>('checking');
  const [pwModalOpen, setPwModalOpen] = useState(false);
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [pwMsg, setPwMsg] = useState<string | null>(null);
  const [pwErr, setPwErr] = useState<string | null>(null);

  useEffect(() => {
    apiRequest<{ status: string }>('/health')
      .then(() => setApiStatus('online'))
      .catch(() => setApiStatus('waking'));
  }, []);

  async function handleChangePassword(e: React.FormEvent) {
    e.preventDefault();
    setPwErr(null);
    setPwMsg(null);
    try {
      await apiRequest(
        '/auth/change-password',
        {
          method: 'POST',
          body: JSON.stringify({
            current_password: currentPassword,
            new_password: newPassword,
          }),
        },
        token,
      );
      setPwMsg('Contraseña actualizada correctamente.');
      setCurrentPassword('');
      setNewPassword('');
    } catch (err) {
      setPwErr(err instanceof Error ? err.message : 'Error cambiando contraseña');
    }
  }

  const navClass = ({ isActive }: { isActive: boolean }) =>
    `group flex items-center gap-3 rounded-xl px-3.5 py-2.5 text-sm font-medium transition-all ${
      isActive
        ? 'bg-indigo-600 text-white shadow-sm shadow-indigo-600/25'
        : 'text-slate-300 hover:bg-slate-800 hover:text-white'
    }`;

  const mobileNavClass = ({ isActive }: { isActive: boolean }) =>
    `shrink-0 rounded-lg px-3 py-1.5 text-xs font-semibold transition ${
      isActive ? 'bg-indigo-600 text-white' : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
    }`;

  const canSeeNav = Boolean(user || isOpenDemo);
  const effectiveRole: UserRole = user?.role || demoRole;

  return (
    <div className="min-h-screen bg-slate-100/70 flex flex-col">
      <header className="no-print sticky top-0 z-30 border-b border-slate-200/80 bg-white/90 backdrop-blur-md">
        <div className="mx-auto flex max-w-[1440px] flex-wrap items-center justify-between gap-3 px-4 py-3 sm:px-6">
          <Link to="/" className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-indigo-600 to-violet-600 text-white shadow-sm">
              <GraduationCap className="h-5 w-5" />
            </div>
            <div>
              <p className="text-sm font-bold tracking-tight text-slate-900">
                Asesor Pedagógico Inteligente
              </p>
              <p className="text-[11px] font-medium text-slate-500">
                Profundización I – IA · Universidad de Manizales
              </p>
            </div>
          </Link>

          <div className="flex flex-wrap items-center gap-2.5">
            <span
              className={`inline-flex items-center gap-1.5 rounded-full border px-3 py-1 text-xs font-semibold ${
                apiStatus === 'online'
                  ? 'border-emerald-200 bg-emerald-50 text-emerald-700'
                  : apiStatus === 'checking'
                    ? 'border-slate-200 bg-slate-100 text-slate-600'
                    : 'border-amber-200 bg-amber-50 text-amber-700'
              }`}
            >
              <span
                className={`h-2 w-2 rounded-full ${
                  apiStatus === 'online'
                    ? 'bg-emerald-500'
                    : apiStatus === 'checking'
                      ? 'bg-slate-400'
                      : 'bg-amber-500 animate-pulse'
                }`}
              />
              {apiStatus === 'online'
                ? 'Backend activo'
                : apiStatus === 'checking'
                  ? 'Conectando...'
                  : 'Activando servidor...'}
            </span>

            {isOpenDemo && !token ? (
              <div className="flex items-center gap-2 rounded-xl border border-slate-200 bg-slate-50 px-3 py-1.5">
                <Sparkles className="h-3.5 w-3.5 text-indigo-600" />
                <span className="text-xs font-medium text-slate-500">Vista:</span>
                <select
                  aria-label="Rol de visualización"
                  value={demoRole}
                  onChange={(e) => switchDemoRole(e.target.value as UserRole)}
                  className="bg-transparent text-xs font-bold text-indigo-700 focus:outline-none cursor-pointer"
                >
                  <option value="teacher">Docente (HITL completo)</option>
                  <option value="student">Estudiante</option>
                  <option value="admin">Administrador</option>
                </select>
              </div>
            ) : user ? (
              <div className="flex flex-wrap items-center gap-2">
                <span className="hidden sm:inline rounded-lg bg-indigo-50 px-2.5 py-1 text-xs font-semibold text-indigo-700">
                  {user.full_name} ({user.role})
                </span>
                <button
                  onClick={() => {
                    setPwMsg(null);
                    setPwErr(null);
                    setPwModalOpen(true);
                  }}
                  className="inline-flex items-center gap-1 rounded-lg border border-slate-200 px-3 py-1.5 text-xs font-medium text-slate-700 hover:bg-slate-100"
                >
                  <KeyRound className="h-3.5 w-3.5" /> Clave
                </button>
                <button
                  onClick={() => logout()}
                  className="inline-flex items-center gap-1 rounded-lg border border-slate-200 px-3 py-1.5 text-xs font-medium text-slate-700 hover:bg-slate-100"
                >
                  <LogOut className="h-3.5 w-3.5" /> Salir
                </button>
              </div>
            ) : (
              <Link
                to="/login"
                className="inline-flex items-center gap-1.5 rounded-xl bg-indigo-600 px-3.5 py-1.5 text-xs font-semibold text-white hover:bg-indigo-700"
              >
                <LogIn className="h-3.5 w-3.5" /> Iniciar sesión
              </Link>
            )}
          </div>
        </div>

        {canSeeNav && (
          <div className="flex gap-2 overflow-x-auto border-t border-slate-100 px-4 py-2 md:hidden">
            <NavLink to="/" end className={mobileNavClass}>Proyecto</NavLink>
            <NavLink to="/portafolio" className={mobileNavClass}>Portafolio</NavLink>
            <NavLink to="/rubricas" className={mobileNavClass}>Rúbricas</NavLink>
            {(effectiveRole === 'teacher' || effectiveRole === 'admin') && (
              <NavLink to="/docente/revision" className={mobileNavClass}>HITL</NavLink>
            )}
            <NavLink to="/informe-integral" className={mobileNavClass}>Integral</NavLink>
            <NavLink to="/mapa-mental" className={mobileNavClass}>Mapa Mental</NavLink>
            <NavLink to="/admin/modelos" className={mobileNavClass}>Modelos</NavLink>
          </div>
        )}
      </header>

      <div className="mx-auto flex w-full max-w-[1440px] flex-1 gap-6 px-4 py-6 sm:px-6">
        <aside className="no-print hidden w-64 shrink-0 md:block">
          <div className="sticky top-20 flex flex-col justify-between rounded-2xl bg-slate-900 p-4 text-slate-100 shadow-lg">
            <nav className="space-y-5">
              <div>
                <p className="px-3 text-[10px] font-bold uppercase tracking-widest text-slate-400">
                  General
                </p>
                <div className="mt-2 space-y-1">
                  <NavLink to="/" end className={navClass}>
                    <BookOpen className="h-4 w-4" /> Proyecto y Equipo
                  </NavLink>
                  {!user && !isOpenDemo && (
                    <NavLink to="/login" className={navClass}>
                      <LogIn className="h-4 w-4" /> Iniciar Sesión
                    </NavLink>
                  )}
                </div>
              </div>

              {canSeeNav && (
                <>
                  <div>
                    <p className="px-3 text-[10px] font-bold uppercase tracking-widest text-slate-400">
                      Evaluación Académica
                    </p>
                    <div className="mt-2 space-y-1">
                      <NavLink to="/portafolio" className={navClass}>
                        <FolderGit2 className="h-4 w-4" /> Portafolio (C1 y C2)
                      </NavLink>
                      <NavLink to="/rubricas" className={navClass}>
                        <ClipboardCheck className="h-4 w-4" /> Gestión de Rúbricas
                      </NavLink>
                      {(effectiveRole === 'teacher' || effectiveRole === 'admin') && (
                        <NavLink to="/docente/revision" className={navClass}>
                          <ShieldCheck className="h-4 w-4" /> Revisión Docente HITL
                        </NavLink>
                      )}
                    </div>
                  </div>

                  <div>
                    <p className="px-3 text-[10px] font-bold uppercase tracking-widest text-slate-400">
                      Analítica y Conocimiento
                    </p>
                    <div className="mt-2 space-y-1">
                      <NavLink to="/informe-integral" className={navClass}>
                        <LineChart className="h-4 w-4" /> Informe Integral
                      </NavLink>
                      <NavLink to="/mapa-mental" className={navClass}>
                        <Network className="h-4 w-4" /> Mapa Mental IA
                      </NavLink>
                      <NavLink to="/admin/modelos" className={navClass}>
                        <Cpu className="h-4 w-4" /> Modelos IA
                      </NavLink>
                    </div>
                  </div>
                </>
              )}
            </nav>

            <div className="mt-6 rounded-xl border border-slate-800 bg-slate-800/60 p-3 text-xs text-slate-300">
              <p className="font-semibold text-white">Seguridad Activa</p>
              <p className="mt-1 text-[11px] text-slate-400">
                JWT + bcrypt + RBAC · Control BOLA/IDOR · Sandbox AST · Cálculo determinista 0,0–5,0.
              </p>
            </div>
          </div>
        </aside>

        <main className="min-w-0 flex-1">
          <Outlet />
        </main>
      </div>

      {pwModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 p-4 backdrop-blur-xs">
          <div className="w-full max-w-md rounded-2xl bg-white p-6 shadow-xl">
            <h2 className="text-lg font-bold text-slate-900">Cambiar contraseña</h2>
            <p className="mt-1 text-xs text-slate-500">
              Debe tener mínimo 8 caracteres, una mayúscula, una minúscula y un número.
            </p>
            <form onSubmit={handleChangePassword} className="mt-4 space-y-3">
              <div>
                <label className="block text-xs font-semibold text-slate-700">Contraseña actual</label>
                <input
                  type="password"
                  required
                  value={currentPassword}
                  onChange={(e) => setCurrentPassword(e.target.value)}
                  className="mt-1 w-full rounded-xl border border-slate-300 px-3 py-2 text-sm"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-700">Nueva contraseña</label>
                <input
                  type="password"
                  required
                  minLength={8}
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  className="mt-1 w-full rounded-xl border border-slate-300 px-3 py-2 text-sm"
                />
              </div>
              {pwErr && (
                <div className="rounded-lg bg-red-50 px-3 py-2 text-xs text-red-700">{pwErr}</div>
              )}
              {pwMsg && (
                <div className="rounded-lg bg-emerald-50 px-3 py-2 text-xs text-emerald-700">{pwMsg}</div>
              )}
              <div className="flex justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setPwModalOpen(false)}
                  className="rounded-xl border border-slate-200 px-4 py-2 text-sm font-medium text-slate-700"
                >
                  Cerrar
                </button>
                <button
                  type="submit"
                  className="rounded-xl bg-indigo-600 px-4 py-2 text-sm font-semibold text-white hover:bg-indigo-700"
                >
                  Actualizar
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
