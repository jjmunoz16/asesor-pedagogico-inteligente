import { useEffect, useState } from 'react';
import { Cpu, Save } from 'lucide-react';
import { apiRequest } from '../api/client';
import { useAuth } from '../auth/AuthContext';

interface ProviderStatus {
  provider: string;
  label: string;
  configured: boolean;
  default_model: string;
  mode: string;
}

export function AdminModelsPage() {
  const { token, user } = useAuth();
  const [activeProvider, setActiveProvider] = useState('gemini');
  const [activeModel, setActiveModel] = useState('');
  const [providers, setProviders] = useState<ProviderStatus[]>([]);
  const [msg, setMsg] = useState<string | null>(null);
  const [err, setErr] = useState<string | null>(null);

  const canEdit = user?.role === 'admin' || user?.role === 'teacher';

  useEffect(() => {
    apiRequest<{
      active_provider: string;
      active_model: string;
      providers: ProviderStatus[];
    }>('/admin/ai-config', {}, token).then((res) => {
      setActiveProvider(res.active_provider);
      setActiveModel(res.active_model);
      setProviders(res.providers);
    });
  }, [token]);

  async function saveConfig(e: React.FormEvent) {
    e.preventDefault();
    setMsg(null);
    setErr(null);
    try {
      await apiRequest(
        '/admin/ai-config',
        {
          method: 'PUT',
          body: JSON.stringify({ active_provider: activeProvider, active_model: activeModel }),
        },
        token,
      );
      setMsg('Configuración de modelo actualizada correctamente.');
    } catch (error) {
      setErr(error instanceof Error ? error.message : 'Error guardando configuración');
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="flex items-center gap-2 text-2xl font-bold text-slate-900">
          <Cpu className="h-6 w-6 text-indigo-600" /> Configuración de Modelos de IA
        </h1>
        <p className="text-sm text-slate-600">
          Arquitectura "modelo intercambiable, harness permanente". Las claves API se gestionan solo en variables de entorno del servidor.
        </p>
      </div>

      {msg && (
        <div className="rounded-xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-800">
          {msg}
        </div>
      )}
      {err && (
        <div className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800">
          {err}
        </div>
      )}

      <div className="grid gap-4 md:grid-cols-2">
        {providers.map((p) => (
          <div
            key={p.provider}
            className={`rounded-2xl border p-4 ${
              activeProvider === p.provider
                ? 'border-indigo-500 bg-indigo-50/40'
                : 'border-slate-200 bg-white'
            }`}
          >
            <div className="flex items-center justify-between">
              <h2 className="text-sm font-bold text-slate-900">{p.label}</h2>
              <span
                className={`rounded-full px-2.5 py-0.5 text-xs font-semibold ${
                  p.configured ? 'bg-emerald-100 text-emerald-800' : 'bg-amber-100 text-amber-800'
                }`}
              >
                {p.configured ? 'Disponible' : 'Sin API key en servidor'}
              </span>
            </div>
            <p className="mt-1 text-xs text-slate-500">
              Modelo por defecto: <code>{p.default_model}</code> · Modo: {p.mode}
            </p>
          </div>
        ))}
      </div>

      <form
        onSubmit={saveConfig}
        className="rounded-2xl border border-slate-200 bg-white p-6 space-y-4 max-w-xl"
      >
        <div>
          <label className="block text-xs font-semibold text-slate-700">Proveedor activo</label>
          <select
            disabled={!canEdit}
            value={activeProvider}
            onChange={(e) => {
              const val = e.target.value;
              setActiveProvider(val);
              const found = providers.find((p) => p.provider === val);
              if (found) setActiveModel(found.default_model);
            }}
            className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm disabled:bg-slate-50"
          >
            {providers.map((p) => (
              <option key={p.provider} value={p.provider}>
                {p.label}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-xs font-semibold text-slate-700">Identificador del modelo</label>
          <input
            disabled={!canEdit}
            value={activeModel}
            onChange={(e) => setActiveModel(e.target.value)}
            className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm disabled:bg-slate-50"
          />
        </div>

        {canEdit && (
          <button
            type="submit"
            className="inline-flex items-center gap-2 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white hover:bg-indigo-700"
          >
            <Save className="h-4 w-4" /> Guardar proveedor activo
          </button>
        )}
      </form>
    </div>
  );
}
