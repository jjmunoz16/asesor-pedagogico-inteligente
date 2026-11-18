import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  CheckCircle2,
  FileCode2,
  FileText,
  FolderOpen,
  Play,
  ShieldAlert,
  Sparkles,
  Upload,
} from 'lucide-react';
import { apiRequest } from '../api/client';
import { useAuth } from '../auth/AuthContext';
import type { ActivityItem } from '../types';

export function PortfolioPage() {
  const { token, user } = useAuth();
  const [activities, setActivities] = useState<ActivityItem[]>([]);
  const [cohortTab, setCohortTab] = useState<'ALL' | 'C1' | 'C2'>('ALL');
  const [loading, setLoading] = useState(true);
  const [evaluatingId, setEvaluatingId] = useState<number | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const [uploadTarget, setUploadTarget] = useState<ActivityItem | null>(null);
  const [groupName, setGroupName] = useState(
    user?.full_name || 'Juan José Muñoz Naranjo & Christopher Villa Noreña',
  );
  const [repoUrl, setRepoUrl] = useState('');
  const [notes, setNotes] = useState('');
  const [selectedFiles, setSelectedFiles] = useState<FileList | null>(null);

  const [newActOpen, setNewActOpen] = useState(false);
  const [actCohortId, setActCohortId] = useState(1);
  const [actSlug, setActSlug] = useState('');
  const [actTitle, setActTitle] = useState('');
  const [actType, setActType] = useState<'lab' | 'exam' | 'colloquium'>('lab');
  const [actObjective, setActObjective] = useState('');
  const [actDescription, setActDescription] = useState('');

  const isPrivileged = user?.role === 'teacher' || user?.role === 'admin';

  async function loadActivities() {
    setLoading(true);
    try {
      const res = await apiRequest<ActivityItem[]>('/portfolio/activities', {}, token);
      setActivities(res);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error cargando portafolio');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadActivities();
  }, [token, user?.role]);

  async function handleEvaluate(act: ActivityItem, providerOverride?: string) {
    if (!act.latest_submission_id) return;
    setEvaluatingId(act.id);
    setError(null);
    setMessage(null);
    try {
      const report = await apiRequest<{ evaluation_id: number }>(
        `/evaluations/submissions/${act.latest_submission_id}/run`,
        {
          method: 'POST',
          body: JSON.stringify(providerOverride ? { provider_override: providerOverride } : {}),
        },
        token,
      );
      setMessage(`Evaluación #${report.evaluation_id} generada para "${act.title}".`);
      await loadActivities();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error ejecutando evaluación');
    } finally {
      setEvaluatingId(null);
    }
  }

  async function handleCreateActivity(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setMessage(null);
    try {
      await apiRequest(
        '/portfolio/activities',
        {
          method: 'POST',
          body: JSON.stringify({
            cohort_id: actCohortId,
            slug: actSlug.trim().toLowerCase(),
            title: actTitle.trim(),
            activity_type: actType,
            official_objective: actObjective.trim() || null,
            description: actDescription.trim(),
          }),
        },
        token,
      );
      setNewActOpen(false);
      setActSlug('');
      setActTitle('');
      setActObjective('');
      setActDescription('');
      setMessage('Actividad académica registrada correctamente.');
      await loadActivities();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error creando actividad');
    }
  }

  async function handleUploadSubmission(e: React.FormEvent) {
    e.preventDefault();
    if (!uploadTarget) return;
    const form = new FormData();
    form.append('student_group_name', groupName);
    if (repoUrl) form.append('repo_url', repoUrl);
    if (notes) form.append('notes', notes);
    if (selectedFiles) {
      Array.from(selectedFiles).forEach((f) => form.append('files', f));
    }
    try {
      await apiRequest(
        `/portfolio/activities/${uploadTarget.id}/submissions`,
        { method: 'POST', body: form },
        token,
      );
      setUploadTarget(null);
      setSelectedFiles(null);
      setRepoUrl('');
      setNotes('');
      await loadActivities();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error subiendo entrega');
    }
  }

  const filtered =
    cohortTab === 'ALL' ? activities : activities.filter((a) => a.cohort_code === cohortTab);

  const evaluatedCount = activities.filter((a) => a.latest_evaluation).length;
  const totalFiles = activities.reduce((acc, a) => acc + a.evidence_count, 0);
  const avgScore =
    evaluatedCount > 0
      ? activities.reduce((acc, a) => {
          const ev = a.latest_evaluation;
          if (!ev) return acc;
          return acc + (ev.final_score_approved ?? ev.calculated_score_ai);
        }, 0) / evaluatedCount
      : null;

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-extrabold tracking-tight text-slate-900">
            Portafolio Académico
          </h1>
          <p className="text-sm text-slate-600">
            Entregas reales de Cohorte 1 (Primer corte) y Cohorte 2 (Segundo corte) verificadas con SHA-256.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          {isPrivileged && (
            <button
              type="button"
              onClick={() => setNewActOpen(true)}
              className="rounded-xl bg-indigo-600 px-3.5 py-2 text-xs font-semibold text-white hover:bg-indigo-700"
            >
              + Nueva Actividad
            </button>
          )}
          <div className="inline-flex rounded-xl border border-slate-200 bg-white p-1 shadow-xs">
          {[
            { id: 'ALL', label: `Todas (${activities.length})` },
            {
              id: 'C1',
              label: `Cohorte 1 (${activities.filter((a) => a.cohort_code === 'C1').length})`,
            },
            {
              id: 'C2',
              label: `Cohorte 2 (${activities.filter((a) => a.cohort_code === 'C2').length})`,
            },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setCohortTab(tab.id as 'ALL' | 'C1' | 'C2')}
              className={`rounded-lg px-3.5 py-2 text-xs sm:text-sm font-semibold transition ${
                cohortTab === tab.id
                  ? 'bg-indigo-600 text-white shadow-xs'
                  : 'text-slate-600 hover:bg-slate-100'
              }`}
            >
              {tab.label}
            </button>
          ))}
          </div>
        </div>
      </div>

      {/* Barra resumen KPI */}
      <div className="grid gap-4 sm:grid-cols-3">
        <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-xs">
          <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">
            Actividades Evaluadas
          </p>
          <p className="mt-1 text-2xl font-extrabold text-slate-900">
            {evaluatedCount} / {activities.length}
          </p>
        </div>
        <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-xs">
          <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">
            Promedio Consolidado
          </p>
          <p className="mt-1 text-2xl font-extrabold text-indigo-700">
            {avgScore !== null ? `${avgScore.toFixed(2)} / 5.00` : 'Pendiente'}
          </p>
        </div>
        <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-xs">
          <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">
            Evidencias con Hash SHA-256
          </p>
          <p className="mt-1 text-2xl font-extrabold text-emerald-700">{totalFiles} archivos</p>
        </div>
      </div>

      {message && (
        <div className="rounded-xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm font-medium text-emerald-800">
          {message}
        </div>
      )}
      {error && (
        <div className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm font-medium text-red-800">
          {error}
        </div>
      )}

      {loading ? (
        <p className="text-sm text-slate-500">Cargando actividades del portafolio...</p>
      ) : (
        <div className="space-y-5">
          {filtered.map((act) => {
            const score = act.latest_evaluation
              ? act.latest_evaluation.final_score_approved ??
                act.latest_evaluation.calculated_score_ai
              : null;

            return (
              <div
                key={act.id}
                className="rounded-2xl border border-slate-200 bg-white p-6 shadow-xs transition hover:border-indigo-200 hover:shadow-md"
              >
                <div className="flex flex-wrap items-start justify-between gap-4">
                  <div className="max-w-2xl space-y-2">
                    <div className="flex flex-wrap items-center gap-2">
                      <span className="inline-flex items-center gap-1 rounded-md bg-indigo-50 px-2.5 py-0.5 text-xs font-bold text-indigo-700">
                        <FolderOpen className="h-3.5 w-3.5" /> {act.cohort_name}
                      </span>
                      <span
                        className={`rounded-md px-2.5 py-0.5 text-xs font-semibold ${
                          act.rubric_is_template
                            ? 'bg-amber-50 text-amber-800'
                            : 'bg-emerald-50 text-emerald-700'
                        }`}
                      >
                        {act.rubric_is_template
                          ? `Rúbrica plantilla editable v${act.rubric_version}`
                          : `Rúbrica validada v${act.rubric_version}`}
                      </span>
                      {act.latest_evaluation && (
                        <span
                          className={`inline-flex items-center gap-1 rounded-md px-2.5 py-0.5 text-xs font-bold ${
                            act.latest_evaluation.status === 'approved'
                              ? 'bg-emerald-100 text-emerald-800'
                              : 'bg-sky-100 text-sky-800'
                          }`}
                        >
                          <CheckCircle2 className="h-3.5 w-3.5" />
                          {act.latest_evaluation.status === 'approved'
                            ? 'Aprobada Docente'
                            : 'Borrador IA'}
                        </span>
                      )}
                    </div>

                    <h2 className="text-lg font-bold text-slate-900">{act.title}</h2>
                    <p className="text-sm text-slate-600">{act.description}</p>

                    <div className="rounded-xl bg-slate-50 px-3.5 py-2.5 text-xs text-slate-700">
                      <span className="font-bold text-slate-900">Objetivo de la actividad: </span>
                      {act.official_objective || (
                        <span className="inline-flex items-center gap-1 text-amber-700">
                          <ShieldAlert className="h-3.5 w-3.5" /> No consta objetivo oficial
                          explícito en la carpeta.
                        </span>
                      )}
                    </div>
                  </div>

                  <div className="flex flex-col items-end gap-3">
                    {score !== null && (
                      <div className="rounded-xl border border-indigo-100 bg-indigo-50 px-4 py-2 text-right">
                        <p className="text-[10px] font-bold uppercase tracking-wider text-indigo-600">
                          Nota calculada
                        </p>
                        <p className="text-2xl font-extrabold text-indigo-900">
                          {score.toFixed(2)} <span className="text-xs font-semibold">/ 5.00</span>
                        </p>
                      </div>
                    )}

                    <div className="flex flex-wrap justify-end gap-2">
                      <button
                        onClick={() => setUploadTarget(act)}
                        className="inline-flex items-center gap-1.5 rounded-xl border border-slate-200 bg-white px-3 py-2 text-xs font-semibold text-slate-700 hover:bg-slate-50"
                      >
                        <Upload className="h-3.5 w-3.5" /> Nueva entrega
                      </button>
                      <button
                        disabled={evaluatingId === act.id || !act.latest_submission_id}
                        onClick={() => handleEvaluate(act)}
                        className="inline-flex items-center gap-1.5 rounded-xl bg-indigo-600 px-3.5 py-2 text-xs font-semibold text-white hover:bg-indigo-700 disabled:opacity-50"
                      >
                        <Sparkles className="h-3.5 w-3.5" />
                        {evaluatingId === act.id ? 'Evaluando...' : 'Evaluar (IA activa)'}
                      </button>
                      <button
                        disabled={evaluatingId === act.id || !act.latest_submission_id}
                        onClick={() => handleEvaluate(act, 'deterministic')}
                        className="inline-flex items-center gap-1.5 rounded-xl border border-indigo-200 bg-indigo-50 px-3 py-2 text-xs font-semibold text-indigo-700 hover:bg-indigo-100 disabled:opacity-50"
                      >
                        <Play className="h-3.5 w-3.5" /> Auditoría Offline
                      </button>
                      {act.latest_evaluation && (
                        <Link
                          to={`/evaluaciones/${act.latest_evaluation.id}`}
                          className="inline-flex items-center gap-1.5 rounded-xl bg-slate-900 px-4 py-2 text-xs font-semibold text-white hover:bg-slate-800"
                        >
                          <FileText className="h-3.5 w-3.5" /> Ver Informe
                        </Link>
                      )}
                    </div>
                  </div>
                </div>

                <div className="mt-4 border-t border-slate-100 pt-4">
                  <p className="text-[11px] font-bold uppercase tracking-wider text-slate-500">
                    Evidencias asociadas ({act.evidence_count})
                  </p>
                  <div className="mt-2.5 grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
                    {act.evidences.map((ev) => (
                      <div
                        key={ev.id}
                        className="flex items-center justify-between rounded-xl border border-slate-200/80 bg-slate-50/70 px-3 py-2 text-xs"
                      >
                        <div className="flex items-center gap-2 min-w-0 pr-2">
                          <FileCode2 className="h-4 w-4 shrink-0 text-slate-400" />
                          <div className="min-w-0">
                            <p className="truncate font-semibold text-slate-800" title={ev.filename}>
                              {ev.filename}
                            </p>
                            <p className="text-[11px] text-slate-500">
                              {ev.file_category} · SHA: {ev.sha256_hash.slice(0, 8)}…
                            </p>
                          </div>
                        </div>
                        <span
                          className={`shrink-0 rounded-md px-2 py-0.5 text-[10px] font-bold ${
                            ev.extraction_status === 'extracted'
                              ? 'bg-emerald-100 text-emerald-700'
                              : 'bg-amber-100 text-amber-800'
                          }`}
                        >
                          {ev.extraction_status === 'extracted' ? 'Texto' : 'Meta'}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {newActOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 p-4 backdrop-blur-xs">
          <div className="w-full max-w-lg rounded-2xl bg-white p-6 shadow-2xl">
            <h3 className="text-lg font-bold text-slate-900">
              Registrar Nueva Actividad Académica
            </h3>
            <form onSubmit={handleCreateActivity} className="mt-4 space-y-3">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-700">Cohorte</label>
                  <select
                    value={actCohortId}
                    onChange={(e) => setActCohortId(Number(e.target.value))}
                    className="mt-1 w-full rounded-xl border border-slate-300 px-3 py-2 text-sm"
                  >
                    <option value={1}>Cohorte 1 (Primer corte)</option>
                    <option value={2}>Cohorte 2 (Segundo corte)</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-700">Tipo</label>
                  <select
                    value={actType}
                    onChange={(e) => setActType(e.target.value as 'lab' | 'exam' | 'colloquium')}
                    className="mt-1 w-full rounded-xl border border-slate-300 px-3 py-2 text-sm"
                  >
                    <option value="lab">Laboratorio</option>
                    <option value="exam">Parcial</option>
                    <option value="colloquium">Coloquio</option>
                  </select>
                </div>
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-700">Identificador (slug)</label>
                <input
                  type="text"
                  required
                  pattern="[a-z0-9-]+"
                  placeholder="lab7-evaluacion"
                  value={actSlug}
                  onChange={(e) => setActSlug(e.target.value)}
                  className="mt-1 w-full rounded-xl border border-slate-300 px-3 py-2 text-sm"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-700">Título de la actividad</label>
                <input
                  type="text"
                  required
                  value={actTitle}
                  onChange={(e) => setActTitle(e.target.value)}
                  className="mt-1 w-full rounded-xl border border-slate-300 px-3 py-2 text-sm"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-700">Objetivo oficial</label>
                <textarea
                  rows={2}
                  value={actObjective}
                  onChange={(e) => setActObjective(e.target.value)}
                  className="mt-1 w-full rounded-xl border border-slate-300 px-3 py-2 text-sm"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-700">Descripción</label>
                <textarea
                  rows={2}
                  value={actDescription}
                  onChange={(e) => setActDescription(e.target.value)}
                  className="mt-1 w-full rounded-xl border border-slate-300 px-3 py-2 text-sm"
                />
              </div>
              <div className="flex justify-end gap-2">
                <button
                  type="button"
                  onClick={() => setNewActOpen(false)}
                  className="rounded-xl border border-slate-200 px-4 py-2 text-sm font-medium text-slate-700"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  className="rounded-xl bg-indigo-600 px-4 py-2 text-sm font-semibold text-white hover:bg-indigo-700"
                >
                  Registrar actividad
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {uploadTarget && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 p-4 backdrop-blur-xs">
          <div className="w-full max-w-lg rounded-2xl bg-white p-6 shadow-2xl">
            <h3 className="text-lg font-bold text-slate-900">
              Cargar nueva entrega — {uploadTarget.title}
            </h3>
            <form onSubmit={handleUploadSubmission} className="mt-4 space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700">
                  Estudiante / Equipo
                </label>
                <input
                  type="text"
                  required
                  value={groupName}
                  onChange={(e) => setGroupName(e.target.value)}
                  className="mt-1 w-full rounded-xl border border-slate-300 px-3 py-2 text-sm"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-700">
                  URL Repositorio GitHub (opcional)
                </label>
                <input
                  type="url"
                  value={repoUrl}
                  onChange={(e) => setRepoUrl(e.target.value)}
                  placeholder="https://github.com/..."
                  className="mt-1 w-full rounded-xl border border-slate-300 px-3 py-2 text-sm"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-700">
                  Archivos (PDF, DOCX, PY, HTML, ZIP, PNG, etc.)
                </label>
                <input
                  type="file"
                  multiple
                  onChange={(e) => setSelectedFiles(e.target.files)}
                  className="mt-1 w-full text-sm text-slate-600"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-700">Notas</label>
                <textarea
                  rows={2}
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  className="mt-1 w-full rounded-xl border border-slate-300 px-3 py-2 text-sm"
                />
              </div>
              <div className="flex justify-end gap-2">
                <button
                  type="button"
                  onClick={() => setUploadTarget(null)}
                  className="rounded-xl border border-slate-200 px-4 py-2 text-sm font-medium text-slate-700"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  className="rounded-xl bg-indigo-600 px-4 py-2 text-sm font-semibold text-white hover:bg-indigo-700"
                >
                  Guardar entrega
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
