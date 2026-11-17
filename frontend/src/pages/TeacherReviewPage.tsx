import { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { CheckCircle, ShieldCheck } from 'lucide-react';
import { apiRequest } from '../api/client';
import { useAuth } from '../auth/AuthContext';
import type { ActivityItem, IndividualReport } from '../types';

export function TeacherReviewPage() {
  const { token } = useAuth();
  const [searchParams, setSearchParams] = useSearchParams();
  const [activities, setActivities] = useState<ActivityItem[]>([]);
  const [report, setReport] = useState<IndividualReport | null>(null);
  const [scores, setScores] = useState<Record<number, number>>({});
  const [notes, setNotes] = useState<Record<number, string>>({});
  const [comments, setComments] = useState('');
  const [feedback, setFeedback] = useState<string | null>(null);

  const selectedEvalId = searchParams.get('evalId');

  useEffect(() => {
    apiRequest<ActivityItem[]>('/portfolio/activities', {}, token).then((acts) => {
      setActivities(acts);
      if (!selectedEvalId) {
        const firstEval = acts.find((a) => a.latest_evaluation)?.latest_evaluation;
        if (firstEval) setSearchParams({ evalId: String(firstEval.id) });
      }
    });
  }, [token]);

  useEffect(() => {
    if (!selectedEvalId) return;
    apiRequest<IndividualReport>(`/evaluations/${selectedEvalId}`, {}, token).then((rep) => {
      setReport(rep);
      const initScores: Record<number, number> = {};
      rep.dimension_cuantificacion.criteria.forEach((c) => {
        initScores[c.criterion_evaluation_id] = c.effective_score;
      });
      setScores(initScores);
    });
  }, [token, selectedEvalId]);

  const liveWeighted =
    report?.dimension_cuantificacion.criteria.reduce((acc, c) => {
      const s = scores[c.criterion_evaluation_id] ?? c.effective_score;
      return acc + s * (c.weight_percent / 100);
    }, 0) ?? 0;

  async function submitDecision(decision: 'approved' | 'adjusted') {
    if (!report) return;
    const adjustments = report.dimension_cuantificacion.criteria.map((c) => ({
      criterion_evaluation_id: c.criterion_evaluation_id,
      teacher_criterion_score: Number(scores[c.criterion_evaluation_id] ?? c.effective_score),
      justification_note: notes[c.criterion_evaluation_id] || '',
    }));

    const updated = await apiRequest<IndividualReport>(
      `/evaluations/${report.evaluation_id}/review`,
      {
        method: 'POST',
        body: JSON.stringify({ decision, comments, adjustments }),
      },
      token,
    );
    setReport(updated);
    setFeedback(
      `Evaluación #${updated.evaluation_id} aprobada con nota oficial ${updated.dimension_cuantificacion.effective_final_score.toFixed(2)} / 5.00.`,
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="flex items-center gap-2 text-2xl font-bold text-slate-900">
            <ShieldCheck className="h-6 w-6 text-indigo-600" /> Revisión Docente HITL (Split-Screen)
          </h1>
          <p className="text-sm text-slate-600">
            Contraste las evidencias reales frente al borrador de IA antes de publicar la nota.
          </p>
        </div>

        <select
          value={selectedEvalId || ''}
          onChange={(e) => setSearchParams({ evalId: e.target.value })}
          className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm"
        >
          <option value="" disabled>
            Seleccione una evaluación...
          </option>
          {activities
            .filter((a) => a.latest_evaluation)
            .map((a) => (
              <option key={a.id} value={a.latest_evaluation!.id}>
                {a.title} (#{a.latest_evaluation!.id} · {a.latest_evaluation!.status})
              </option>
            ))}
        </select>
      </div>

      {feedback && (
        <div className="rounded-xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm font-medium text-emerald-800">
          {feedback}
        </div>
      )}

      {!report ? (
        <div className="rounded-xl border border-slate-200 bg-white p-8 text-center text-sm text-slate-500">
          Ejecute primero una evaluación desde el Portafolio para revisarla aquí.
        </div>
      ) : (
        <div className="grid gap-6 lg:grid-cols-2">
          {/* Panel Izquierdo: Evidencias reales */}
          <div className="space-y-4 rounded-2xl border border-slate-200 bg-white p-5 shadow-xs">
            <h2 className="text-base font-bold text-slate-900">
              Evidencias Extraídas ({report.submission.evidences.length})
            </h2>
            <div className="max-h-[600px] space-y-3 overflow-y-auto pr-1">
              {report.submission.evidences.map((ev) => (
                <div key={ev.id} className="rounded-xl border border-slate-200 bg-slate-50 p-3">
                  <p className="text-xs font-bold text-slate-900">
                    {ev.filename}{' '}
                    <span className="font-normal text-slate-500">({ev.extraction_status})</span>
                  </p>
                  <pre className="mt-2 max-h-48 overflow-auto whitespace-pre-wrap text-[11px] text-slate-700">
                    {ev.extracted_text_summary || 'Sin extracto textual.'}
                  </pre>
                </div>
              ))}
            </div>
          </div>

          {/* Panel Derecho: Ajuste y aprobación docente */}
          <div className="space-y-4 rounded-2xl border border-slate-200 bg-white p-5 shadow-xs">
            <div className="flex items-center justify-between">
              <h2 className="text-base font-bold text-slate-900">Dictamen por Criterio</h2>
              <span className="rounded-lg bg-indigo-50 px-3 py-1 text-sm font-bold text-indigo-800">
                Nota recalculada: {liveWeighted.toFixed(2)} / 5.00
              </span>
            </div>

            <div className="space-y-3">
              {report.dimension_cuantificacion.criteria.map((c) => (
                <div key={c.criterion_evaluation_id} className="rounded-xl border border-slate-200 p-3">
                  <div className="flex items-center justify-between gap-2">
                    <p className="text-xs font-bold text-slate-900">
                      {c.criterion_name} ({c.weight_percent} %)
                    </p>
                    <input
                      type="number"
                      step="0.1"
                      min="0"
                      max="5"
                      value={scores[c.criterion_evaluation_id] ?? c.effective_score}
                      onChange={(e) =>
                        setScores((prev) => ({
                          ...prev,
                          [c.criterion_evaluation_id]: Math.max(0, Math.min(5, Number(e.target.value))),
                        }))
                      }
                      className="w-20 rounded border border-slate-300 px-2 py-1 text-sm font-bold"
                    />
                  </div>
                  <p className="mt-1 text-xs text-slate-600">{c.justification}</p>
                  <input
                    type="text"
                    placeholder="Nota u observación docente (opcional)"
                    value={notes[c.criterion_evaluation_id] || ''}
                    onChange={(e) =>
                      setNotes((prev) => ({ ...prev, [c.criterion_evaluation_id]: e.target.value }))
                    }
                    className="mt-2 w-full rounded border border-slate-200 px-2.5 py-1 text-xs"
                  />
                </div>
              ))}
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700">
                Observación general del docente
              </label>
              <textarea
                rows={2}
                value={comments}
                onChange={(e) => setComments(e.target.value)}
                className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
                placeholder="Retroalimentación final del docente..."
              />
            </div>

            <div className="flex flex-wrap gap-3">
              <button
                onClick={() => submitDecision('adjusted')}
                className="inline-flex flex-1 items-center justify-center gap-2 rounded-lg bg-emerald-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-emerald-700"
              >
                <CheckCircle className="h-4 w-4" /> Aprobar y Publicar Evaluación
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
