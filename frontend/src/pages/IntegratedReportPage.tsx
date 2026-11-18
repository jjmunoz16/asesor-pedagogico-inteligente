import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Award, BarChart3, Download, Printer, TrendingUp } from 'lucide-react';
import { apiDownloadBlob, apiRequest } from '../api/client';
import { useAuth } from '../auth/AuthContext';
import type { IntegratedReport } from '../types';

export function IntegratedReportPage() {
  const { token } = useAuth();
  const [data, setData] = useState<IntegratedReport | null>(null);
  const [errMsg, setErrMsg] = useState<string | null>(null);

  useEffect(() => {
    apiRequest<IntegratedReport>('/reports/integrated', {}, token).then(setData);
  }, [token]);

  async function downloadPdf() {
    try {
      setErrMsg(null);
      await apiDownloadBlob('/reports/integrated/pdf', 'informe_integral_aprendizaje.pdf', token);
    } catch (err) {
      setErrMsg(err instanceof Error ? err.message : 'Error descargando PDF');
    }
  }

  async function downloadMarkdown() {
    try {
      setErrMsg(null);
      await apiDownloadBlob('/reports/integrated/markdown', 'informe_integral_aprendizaje.md', token);
    } catch (err) {
      setErrMsg(err instanceof Error ? err.message : 'Error descargando Markdown');
    }
  }

  function downloadJson() {
    if (!data) return;
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'informe_integral_aprendizaje.json';
    a.click();
    URL.revokeObjectURL(url);
  }

  if (!data) return <p className="text-sm text-slate-500">Consolidando informe integral...</p>;

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-extrabold tracking-tight text-slate-900">
            Informe Integral del Aprendizaje
          </h1>
          <p className="text-sm text-slate-600">
            Consolidado global de competencias, evolución entre Cohortes 1 y 2 y plan de fortalecimiento.
          </p>
        </div>
        <div className="no-print flex flex-wrap gap-2">
          <button
            onClick={downloadPdf}
            className="inline-flex items-center gap-1.5 rounded-xl bg-indigo-600 px-3.5 py-2 text-xs font-semibold text-white hover:bg-indigo-700"
          >
            <Download className="h-4 w-4" /> Descargar PDF
          </button>
          <button
            onClick={downloadMarkdown}
            className="inline-flex items-center gap-1.5 rounded-xl border border-slate-200 bg-white px-3.5 py-2 text-xs font-semibold text-slate-700 hover:bg-slate-50"
          >
            <Download className="h-4 w-4" /> .MD
          </button>
          <button
            onClick={downloadJson}
            className="inline-flex items-center gap-1.5 rounded-xl bg-slate-900 px-3.5 py-2 text-xs font-semibold text-white hover:bg-slate-800"
          >
            <Download className="h-4 w-4" /> .JSON
          </button>
          <button
            onClick={() => window.print()}
            className="inline-flex items-center gap-1.5 rounded-xl border border-slate-200 bg-white px-3.5 py-2 text-xs font-semibold text-slate-700 hover:bg-slate-50"
          >
            <Printer className="h-4 w-4" /> Imprimir
          </button>
        </div>
      </div>

      {errMsg && (
        <div className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {errMsg}
        </div>
      )}

      <div className="grid gap-4 sm:grid-cols-3">
        <div className="print-container rounded-2xl bg-gradient-to-br from-indigo-600 to-violet-700 p-5 text-white shadow-md">
          <div className="flex items-center justify-between">
            <p className="text-xs font-bold uppercase tracking-wider text-indigo-100">
              Promedio Global
            </p>
            <Award className="h-5 w-5 text-indigo-200" />
          </div>
          <p className="mt-2 text-4xl font-extrabold">
            {data.global_average !== null ? `${data.global_average.toFixed(2)}` : '—'}
            <span className="text-base font-semibold text-indigo-200"> / 5.00</span>
          </p>
        </div>

        <div className="print-container rounded-2xl border border-slate-200 bg-white p-5 shadow-xs">
          <div className="flex items-center justify-between">
            <p className="text-xs font-bold uppercase tracking-wider text-slate-500">
              Actividades Evaluadas
            </p>
            <BarChart3 className="h-5 w-5 text-indigo-500" />
          </div>
          <p className="mt-2 text-3xl font-extrabold text-slate-900">
            {data.evaluated_activities} / {data.total_activities}
          </p>
        </div>

        <div className="print-container rounded-2xl border border-slate-200 bg-white p-5 shadow-xs">
          <div className="flex items-center justify-between">
            <p className="text-xs font-bold uppercase tracking-wider text-slate-500">
              Evolución entre Cohortes
            </p>
            <TrendingUp className="h-5 w-5 text-emerald-500" />
          </div>
          <div className="mt-3 space-y-2.5">
            {data.cohort_evolution.map((ce) => {
              const pct = ce.average_score !== null ? (ce.average_score / 5) * 100 : 0;
              return (
                <div key={ce.cohort_code}>
                  <div className="flex justify-between text-xs font-semibold">
                    <span className="text-slate-700">{ce.cohort_name}</span>
                    <span className="text-indigo-700">
                      {ce.average_score !== null ? `${ce.average_score.toFixed(2)}` : 'Sin evaluar'}
                    </span>
                  </div>
                  <div className="mt-1 h-2 w-full overflow-hidden rounded-full bg-slate-100">
                    <div
                      className="h-full rounded-full bg-emerald-500"
                      style={{ width: `${pct}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      <div className="print-container rounded-2xl border border-slate-200 bg-white p-6 shadow-xs">
        <h2 className="text-lg font-bold text-slate-900">Desempeño por Actividad</h2>
        <div className="mt-4 space-y-3">
          {data.activities.map((a) => {
            const pct = a.score !== null ? (a.score / 5) * 100 : 0;
            return (
              <div
                key={a.activity_id}
                className="flex flex-wrap items-center justify-between gap-4 rounded-xl border border-slate-100 bg-slate-50/70 p-3.5"
              >
                <div className="min-w-[240px] flex-1">
                  <div className="flex items-center gap-2">
                    <span className="rounded bg-indigo-100 px-2 py-0.5 text-[11px] font-bold text-indigo-800">
                      {a.cohort_code}
                    </span>
                    <p className="text-sm font-bold text-slate-900">{a.title}</p>
                  </div>
                  <div className="mt-2 h-2 w-full overflow-hidden rounded-full bg-slate-200">
                    <div
                      className="h-full rounded-full bg-indigo-600"
                      style={{ width: `${pct}%` }}
                    />
                  </div>
                </div>

                <div className="flex items-center gap-4">
                  <span className="rounded-full bg-white px-2.5 py-0.5 text-xs font-semibold text-slate-600 border border-slate-200">
                    {a.status}
                  </span>
                  <span className="w-14 text-right text-base font-extrabold text-slate-900">
                    {a.score !== null ? a.score.toFixed(2) : '—'}
                  </span>
                  {a.evaluation_id && (
                    <Link
                      to={`/evaluaciones/${a.evaluation_id}`}
                      className="no-print rounded-lg bg-slate-900 px-3 py-1.5 text-xs font-semibold text-white hover:bg-slate-800"
                    >
                      Abrir
                    </Link>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <div className="print-container rounded-2xl border border-slate-200 bg-white p-6 shadow-xs">
          <h2 className="text-base font-bold text-slate-900">Competencias Desarrolladas</h2>
          {data.competencies.length === 0 ? (
            <p className="mt-2 text-sm text-slate-500">
              Evalúa al menos una actividad en el Portafolio para calcular niveles de dominio reales.
            </p>
          ) : (
            <div className="mt-4 space-y-3">
              {data.competencies.map((c) => {
                const pct = (c.average_score / 5) * 100;
                return (
                  <div key={c.competency} className="rounded-xl bg-slate-50 p-3">
                    <div className="flex items-center justify-between text-sm">
                      <span className="font-semibold text-slate-800">{c.competency}</span>
                      <span className="font-extrabold text-indigo-700">
                        {c.average_score.toFixed(2)} · {c.mastery_level}
                      </span>
                    </div>
                    <div className="mt-1.5 h-2 w-full overflow-hidden rounded-full bg-slate-200">
                      <div
                        className="h-full rounded-full bg-emerald-500"
                        style={{ width: `${pct}%` }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        <div className="print-container rounded-2xl border border-slate-200 bg-white p-6 shadow-xs">
          <h2 className="text-base font-bold text-slate-900">
            Plan Personalizado de Fortalecimiento
          </h2>
          {data.strengthening_plan.length === 0 ? (
            <p className="mt-2 text-sm text-slate-500">
              Se generará automáticamente a partir de las recomendaciones de las actividades evaluadas.
            </p>
          ) : (
            <ul className="mt-3 list-disc pl-5 text-sm text-slate-700 space-y-2">
              {data.strengthening_plan.map((p, i) => (
                <li key={i}>{p}</li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  );
}
