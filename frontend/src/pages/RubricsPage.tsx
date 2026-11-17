import { useEffect, useState } from 'react';
import { AlertTriangle, CheckCircle2, Plus, Save, Trash2 } from 'lucide-react';
import { apiRequest } from '../api/client';
import { useAuth } from '../auth/AuthContext';
import type { ActivityItem, RubricCriterionItem, RubricResponse } from '../types';

export function RubricsPage() {
  const { token, user } = useAuth();
  const [activities, setActivities] = useState<ActivityItem[]>([]);
  const [selectedActivityId, setSelectedActivityId] = useState<number | null>(null);
  const [rubricName, setRubricName] = useState('');
  const [notes, setNotes] = useState('');
  const [isTemplate, setIsTemplate] = useState(true);
  const [criteria, setCriteria] = useState<RubricCriterionItem[]>([]);
  const [versions, setVersions] = useState<Array<{ version_number: number; created_at: string }>>([]);
  const [statusMsg, setStatusMsg] = useState<string | null>(null);
  const [errMsg, setErrMsg] = useState<string | null>(null);

  const canEdit = user?.role === 'teacher' || user?.role === 'admin';
  const totalWeight = Math.round(criteria.reduce((acc, c) => acc + Number(c.weight_percent || 0), 0) * 100) / 100;
  const isWeightValid = Math.abs(totalWeight - 100) <= 0.01 && criteria.length > 0;

  useEffect(() => {
    apiRequest<ActivityItem[]>('/portfolio/activities', {}, token).then((acts) => {
      setActivities(acts);
      if (acts.length > 0) setSelectedActivityId(acts[0].id);
    });
  }, [token, user?.role]);

  useEffect(() => {
    if (!selectedActivityId) return;
    setStatusMsg(null);
    setErrMsg(null);
    apiRequest<RubricResponse>(`/rubrics/activity/${selectedActivityId}`, {}, token).then((res) => {
      if (res.rubric) {
        setRubricName(res.rubric.name);
        setIsTemplate(res.rubric.is_template_proposal);
        setNotes(res.rubric.active_version.notes);
        setCriteria(res.rubric.active_version.criteria);
        setVersions(res.rubric.versions_history);
      } else {
        setRubricName('Nueva Rúbrica');
        setCriteria([]);
        setVersions([]);
      }
    });
  }, [token, selectedActivityId]);

  function addCriterion() {
    setCriteria((prev) => [
      ...prev,
      {
        code: `CRIT-${prev.length + 1}`,
        competency_name: 'Competencia IA',
        criterion_name: 'Nuevo criterio',
        description: 'Descripción del criterio',
        weight_percent: 0,
        performance_levels: {
          'No evidencia': 0.0,
          Insuficiente: 1.5,
          Básico: 3.0,
          Satisfactorio: 4.0,
          Sobresaliente: 5.0,
        },
      },
    ]);
  }

  async function saveNewVersion() {
    if (!selectedActivityId || !isWeightValid) return;
    setErrMsg(null);
    setStatusMsg(null);
    try {
      const res = await apiRequest<{ version_number: number }>(
        '/rubrics',
        {
          method: 'POST',
          body: JSON.stringify({
            activity_id: selectedActivityId,
            name: rubricName,
            is_template_proposal: false,
            notes,
            criteria,
          }),
        },
        token,
      );
      setStatusMsg(`Guardada versión v${res.version_number} con ponderación exacta del 100 %.`);
      setIsTemplate(false);
    } catch (err) {
      setErrMsg(err instanceof Error ? err.message : 'Error guardando rúbrica');
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Gestión y Versionado de Rúbricas</h1>
          <p className="text-sm text-slate-600">
            Validador estricto al 100 % y preservación de versiones históricas.
          </p>
        </div>

        <select
          value={selectedActivityId ?? ''}
          onChange={(e) => setSelectedActivityId(Number(e.target.value))}
          className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm font-medium"
        >
          {activities.map((a) => (
            <option key={a.id} value={a.id}>
              {a.cohort_code} · {a.title}
            </option>
          ))}
        </select>
      </div>

      {isTemplate && (
        <div className="flex items-start gap-3 rounded-xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-900">
          <AlertTriangle className="mt-0.5 h-5 w-5 shrink-0 text-amber-600" />
          <div>
            <strong>Plantilla base editable (DP-16):</strong> Esta rúbrica es una propuesta inicial del
            equipo alineada con las 3 dimensiones de evaluación (el documento oficial del profesor no
            incluye pesos específicos por laboratorio). Un docente puede editarla y guardar una nueva versión.
          </div>
        </div>
      )}

      <div
        className={`flex flex-wrap items-center justify-between gap-4 rounded-xl border p-4 ${
          isWeightValid
            ? 'border-emerald-200 bg-emerald-50 text-emerald-900'
            : 'border-red-200 bg-red-50 text-red-900'
        }`}
      >
        <div className="flex items-center gap-2 text-sm font-semibold">
          {isWeightValid ? (
            <CheckCircle2 className="h-5 w-5 text-emerald-600" />
          ) : (
            <AlertTriangle className="h-5 w-5 text-red-600" />
          )}
          Suma actual de ponderaciones: {totalWeight.toFixed(2)} % / 100 %
          {!isWeightValid && ' — Ajuste los pesos para alcanzar 100 % exacto.'}
        </div>

        {canEdit && (
          <div className="flex gap-2">
            <button
              type="button"
              onClick={addCriterion}
              className="inline-flex items-center gap-1 rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-xs font-semibold text-slate-700 hover:bg-slate-50"
            >
              <Plus className="h-3.5 w-3.5" /> Criterio
            </button>
            <button
              type="button"
              disabled={!isWeightValid}
              onClick={saveNewVersion}
              className="inline-flex items-center gap-1.5 rounded-lg bg-indigo-600 px-3.5 py-1.5 text-xs font-semibold text-white hover:bg-indigo-700 disabled:opacity-40"
            >
              <Save className="h-3.5 w-3.5" /> Guardar nueva versión
            </button>
          </div>
        )}
      </div>

      {statusMsg && (
        <div className="rounded-lg border border-emerald-200 bg-emerald-50 px-4 py-2 text-sm text-emerald-800">
          {statusMsg}
        </div>
      )}
      {errMsg && (
        <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-2 text-sm text-red-800">
          {errMsg}
        </div>
      )}

      <div className="space-y-3 rounded-2xl border border-slate-200 bg-white p-6 shadow-xs">
        <div className="grid gap-4 sm:grid-cols-2">
          <div>
            <label className="block text-xs font-semibold text-slate-600">Nombre de la rúbrica</label>
            <input
              type="text"
              disabled={!canEdit}
              value={rubricName}
              onChange={(e) => setRubricName(e.target.value)}
              className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm disabled:bg-slate-50"
            />
          </div>
          <div>
            <label className="block text-xs font-semibold text-slate-600">Versiones registradas</label>
            <p className="mt-2 text-sm text-slate-700">
              {versions.map((v) => `v${v.version_number}`).join(' · ') || 'Sin versiones'}
            </p>
          </div>
        </div>

        <div className="overflow-x-auto pt-2">
          <table className="w-full text-left text-sm">
            <thead>
              <tr className="border-b border-slate-200 text-xs uppercase text-slate-500">
                <th className="py-2 pr-3">Código</th>
                <th className="py-2 pr-3">Competencia</th>
                <th className="py-2 pr-3">Criterio y descriptor</th>
                <th className="py-2 pr-3 w-28">Peso (%)</th>
                {canEdit && <th className="py-2 w-12" />}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {criteria.map((c, idx) => (
                <tr key={`${c.code}-${idx}`}>
                  <td className="py-3 pr-3 align-top">
                    <input
                      disabled={!canEdit}
                      value={c.code}
                      onChange={(e) =>
                        setCriteria((prev) =>
                          prev.map((item, i) => (i === idx ? { ...item, code: e.target.value } : item)),
                        )
                      }
                      className="w-28 rounded border border-slate-300 px-2 py-1 text-xs font-mono disabled:bg-slate-50"
                    />
                  </td>
                  <td className="py-3 pr-3 align-top">
                    <input
                      disabled={!canEdit}
                      value={c.competency_name}
                      onChange={(e) =>
                        setCriteria((prev) =>
                          prev.map((item, i) =>
                            i === idx ? { ...item, competency_name: e.target.value } : item,
                          ),
                        )
                      }
                      className="w-full rounded border border-slate-300 px-2 py-1 text-xs disabled:bg-slate-50"
                    />
                  </td>
                  <td className="py-3 pr-3 align-top space-y-1">
                    <input
                      disabled={!canEdit}
                      value={c.criterion_name}
                      onChange={(e) =>
                        setCriteria((prev) =>
                          prev.map((item, i) =>
                            i === idx ? { ...item, criterion_name: e.target.value } : item,
                          ),
                        )
                      }
                      className="w-full rounded border border-slate-300 px-2 py-1 text-xs font-semibold disabled:bg-slate-50"
                    />
                    <textarea
                      disabled={!canEdit}
                      rows={2}
                      value={c.description}
                      onChange={(e) =>
                        setCriteria((prev) =>
                          prev.map((item, i) =>
                            i === idx ? { ...item, description: e.target.value } : item,
                          ),
                        )
                      }
                      className="w-full rounded border border-slate-300 px-2 py-1 text-xs text-slate-600 disabled:bg-slate-50"
                    />
                  </td>
                  <td className="py-3 pr-3 align-top">
                    <input
                      type="number"
                      step="0.5"
                      min="0"
                      max="100"
                      disabled={!canEdit}
                      value={c.weight_percent}
                      onChange={(e) =>
                        setCriteria((prev) =>
                          prev.map((item, i) =>
                            i === idx ? { ...item, weight_percent: Number(e.target.value) } : item,
                          ),
                        )
                      }
                      className="w-24 rounded border border-slate-300 px-2 py-1 text-sm font-semibold disabled:bg-slate-50"
                    />
                  </td>
                  {canEdit && (
                    <td className="py-3 align-top">
                      <button
                        type="button"
                        onClick={() => setCriteria((prev) => prev.filter((_, i) => i !== idx))}
                        className="rounded p-1 text-slate-400 hover:bg-red-50 hover:text-red-600"
                        title="Eliminar criterio"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </td>
                  )}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
