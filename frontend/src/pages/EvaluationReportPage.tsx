import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import {
  CheckCircle2,
  Download,
  FileCheck,
  Printer,
  ShieldCheck,
  Terminal,
} from 'lucide-react';
import { apiDownloadBlob, apiRequest } from '../api/client';
import { useAuth } from '../auth/AuthContext';
import type { IndividualReport } from '../types';

export function EvaluationReportPage() {
  const { evaluationId } = useParams<{ evaluationId: string }>();
  const { token, user } = useAuth();
  const [report, setReport] = useState<IndividualReport | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!evaluationId) return;
    apiRequest<IndividualReport>(`/evaluations/${evaluationId}`, {}, token)
      .then(setReport)
      .catch((err) => setError(err instanceof Error ? err.message : 'Error cargando informe'));
  }, [token, evaluationId]);

  async function downloadPdf() {
    if (!evaluationId) return;
    try {
      await apiDownloadBlob(
        `/evaluations/${evaluationId}/pdf`,
        `informe_evaluacion_${evaluationId}.pdf`,
        token,
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error descargando PDF');
    }
  }

  async function downloadMarkdown() {
    if (!evaluationId) return;
    try {
      await apiDownloadBlob(
        `/evaluations/${evaluationId}/markdown`,
        `informe_evaluacion_${evaluationId}.md`,
        token,
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error descargando Markdown');
    }
  }

  function downloadJson() {
    if (!report) return;
    const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `informe_evaluacion_${report.evaluation_id}.json`;
    a.click();
    URL.revokeObjectURL(url);
  }

  if (error) {
    return (
      <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
        {error}
      </div>
    );
  }
  if (!report) {
    return <p className="text-sm text-slate-500">Cargando informe individual...</p>;
  }

  const ver = report.dimension_verificacion;
  const quant = report.dimension_cuantificacion;
  const rec = report.dimension_recomendacion;
  const sb = report.verificacion_tecnica_sandbox;

  return (
    <div className="space-y-6">
      <div className="print-container rounded-3xl border border-slate-200 bg-white p-6 sm:p-8 shadow-xs">
        <div className="flex flex-wrap items-start justify-between gap-6">
          <div className="space-y-2 max-w-2xl">
            <span className="inline-block rounded-full bg-indigo-50 px-3 py-1 text-xs font-bold uppercase tracking-wider text-indigo-700">
              {report.activity.cohort} · Informe Individual
            </span>
            <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-slate-900">
              {report.activity.title}
            </h1>
            <p className="text-sm text-slate-600">
              Grupo: <strong>{report.submission.student_group_name}</strong> · Rúbrica:{' '}
              {report.traceability.rubric_name} (v{report.traceability.rubric_version})
            </p>
            <div className="flex flex-wrap items-center gap-2 pt-1 text-xs text-slate-500">
              <span>
                Motor:{' '}
                <code className="rounded bg-slate-100 px-1.5 py-0.5 text-slate-800">
                  {report.traceability.ai_provider} / {report.traceability.ai_model}
                </code>
              </span>
              <span
                className={`inline-block rounded-full px-2.5 py-0.5 font-bold ${
                  report.status === 'approved'
                    ? 'bg-emerald-100 text-emerald-800'
                    : 'bg-sky-100 text-sky-800'
                }`}
              >
                {report.status === 'approved'
                  ? 'Aprobada por Docente'
                  : 'Borrador IA (pendiente HITL)'}
              </span>
            </div>
          </div>

          <div className="flex flex-col items-end gap-3">
            <div className="rounded-2xl bg-gradient-to-br from-indigo-600 to-violet-700 px-6 py-4 text-center text-white shadow-md">
              <p className="text-[11px] font-bold uppercase tracking-wider text-indigo-100">
                Nota Final (0,0–5,0)
              </p>
              <p className="mt-0.5 text-4xl font-extrabold">
                {quant.effective_final_score.toFixed(2)}
              </p>
              <p className="text-[10px] text-indigo-200">Cálculo determinista en backend</p>
            </div>

            <div className="no-print flex flex-wrap justify-end gap-2">
              <button
                onClick={downloadPdf}
                className="inline-flex items-center gap-1.5 rounded-xl bg-slate-900 px-3 py-1.5 text-xs font-semibold text-white hover:bg-slate-800"
              >
                <Download className="h-3.5 w-3.5" /> Descargar PDF
              </button>
              <button
                onClick={downloadMarkdown}
                className="inline-flex items-center gap-1.5 rounded-xl border border-slate-200 bg-white px-3 py-1.5 text-xs font-semibold text-slate-700 hover:bg-slate-50"
              >
                <Download className="h-3.5 w-3.5" /> .MD
              </button>
              <button
                onClick={downloadJson}
                className="inline-flex items-center gap-1.5 rounded-xl border border-slate-200 bg-white px-3 py-1.5 text-xs font-semibold text-slate-700 hover:bg-slate-50"
              >
                <Download className="h-3.5 w-3.5" /> .JSON
              </button>
              <button
                onClick={() => window.print()}
                className="inline-flex items-center gap-1.5 rounded-xl border border-slate-200 bg-white px-3 py-1.5 text-xs font-semibold text-slate-700 hover:bg-slate-50"
              >
                <Printer className="h-3.5 w-3.5" /> Imprimir
              </button>
              {(user?.role === 'teacher' || user?.role === 'admin') && (
                <Link
                  to={`/docente/revision?evalId=${report.evaluation_id}`}
                  className="inline-flex items-center gap-1.5 rounded-xl bg-indigo-600 px-3.5 py-1.5 text-xs font-semibold text-white hover:bg-indigo-700"
                >
                  <ShieldCheck className="h-3.5 w-3.5" /> Revisar HITL
                </Link>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Dimensión 1: VERIFICACIÓN */}
      <section className="print-container rounded-2xl border border-slate-200 bg-white p-6 shadow-xs space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <h2 className="flex items-center gap-2 text-lg font-bold text-slate-900">
            <FileCheck className="h-5 w-5 text-indigo-600" /> 1. VERIFICACIÓN (Cumplimiento de Objetivo)
          </h2>
          <span className="rounded-full bg-emerald-100 px-3 py-1 text-xs font-bold uppercase text-emerald-800">
            {ver.objetivo_cumplido}
          </span>
        </div>
        <div className="rounded-xl bg-slate-50 p-3.5 text-sm text-slate-700">
          <strong>Objetivo de la actividad:</strong>{' '}
          {report.activity.official_objective || 'No consta objetivo oficial explícito en las evidencias.'}
        </div>
        <p className="text-sm leading-relaxed text-slate-700">{ver.resumen_verificacion}</p>

        <div>
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500">
            Evidencias citadas ({ver.evidencias_citadas.length})
          </h3>
          <div className="mt-2 grid gap-2.5 md:grid-cols-2">
            {ver.evidencias_citadas.map((ev, idx) => (
              <div key={idx} className="rounded-xl border border-slate-200 bg-slate-50/70 p-3 text-xs">
                <p className="font-bold text-slate-900">
                  {ev.archivo} <span className="font-normal text-slate-500">({ev.ubicacion})</span>
                </p>
                <p className="mt-1 text-slate-700 line-clamp-3">“{ev.fragmento}”</p>
              </div>
            ))}
          </div>
        </div>

        {ver.faltantes_detectados.length > 0 && (
          <div className="rounded-xl border border-amber-200 bg-amber-50 p-3.5 text-xs text-amber-900">
            <strong>Observaciones / archivos sin extracción textual:</strong>
            <ul className="mt-1 list-disc pl-5 space-y-0.5">
              {ver.faltantes_detectados.map((f, i) => (
                <li key={i}>{f}</li>
              ))}
            </ul>
          </div>
        )}
      </section>

      {/* Verificación Técnica Sandbox */}
      <section className="print-container rounded-2xl border border-slate-200 bg-white p-6 shadow-xs space-y-3">
        <h2 className="flex items-center gap-2 text-lg font-bold text-slate-900">
          <Terminal className="h-5 w-5 text-slate-700" /> Verificación Técnica Objetiva (Sandbox)
        </h2>
        <div className="flex flex-wrap gap-2.5 text-xs">
          <span className="rounded-lg bg-slate-100 px-3 py-1.5 font-medium">
            Modo: <code>{sb.sandbox_mode || 'N/A'}</code>
          </span>
          <span
            className={`rounded-lg px-3 py-1.5 font-semibold ${
              sb.syntax_valid ? 'bg-emerald-100 text-emerald-800' : 'bg-red-100 text-red-800'
            }`}
          >
            Sintaxis: {sb.syntax_valid ? 'Válida' : 'Con errores'}
          </span>
          <span className="rounded-lg bg-slate-100 px-3 py-1.5">
            Archivos analizados: {sb.files_checked.length} · Tiempo: {sb.execution_time_ms} ms
          </span>
          {sb.unit_tests_total !== null && (
            <span className="rounded-lg bg-emerald-100 px-3 py-1.5 font-semibold text-emerald-800">
              Tests: {sb.unit_tests_passed}/{sb.unit_tests_total}
            </span>
          )}
        </div>
        {sb.static_findings.length > 0 && (
          <ul className="list-disc pl-5 text-xs text-amber-800 space-y-0.5">
            {sb.static_findings.map((f, i) => (
              <li key={i}>{f}</li>
            ))}
          </ul>
        )}
      </section>

      {/* Dimensión 2: CUANTIFICACIÓN */}
      <section className="print-container rounded-2xl border border-slate-200 bg-white p-6 shadow-xs space-y-4">
        <h2 className="flex items-center gap-2 text-lg font-bold text-slate-900">
          <CheckCircle2 className="h-5 w-5 text-emerald-600" /> 2. CUANTIFICACIÓN (Rúbrica Ponderada)
        </h2>
        <div className="space-y-3">
          {quant.criteria.map((c) => {
            const pct = Math.min(100, Math.max(0, (c.effective_score / 5) * 100));
            return (
              <div
                key={c.criterion_evaluation_id}
                className="rounded-xl border border-slate-200 bg-slate-50/60 p-4"
              >
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <div>
                    <span className="text-[11px] font-bold uppercase text-indigo-600">
                      {c.competency_name} · Peso {c.weight_percent} %
                    </span>
                    <h3 className="text-sm font-bold text-slate-900">{c.criterion_name}</h3>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="rounded-full bg-white px-2.5 py-0.5 text-xs font-semibold text-slate-700 border border-slate-200">
                      {c.ai_level_label}
                    </span>
                    <span className="text-base font-extrabold text-indigo-700">
                      {c.effective_score.toFixed(2)} / 5.00
                    </span>
                  </div>
                </div>
                <div className="mt-2 h-2 w-full overflow-hidden rounded-full bg-slate-200">
                  <div
                    className="h-full rounded-full bg-indigo-600"
                    style={{ width: `${pct}%` }}
                  />
                </div>
                <p className="mt-2 text-xs text-slate-600">
                  {c.justification}{' '}
                  <strong className="text-slate-800">
                    (Aporte ponderado: +{c.weighted_contribution.toFixed(2)})
                  </strong>
                </p>
              </div>
            );
          })}
        </div>
      </section>

      {/* Dimensión 3: RECOMENDACIÓN */}
      <section className="print-container rounded-2xl border border-slate-200 bg-white p-6 shadow-xs space-y-4">
        <h2 className="text-lg font-bold text-slate-900">3. RECOMENDACIÓN</h2>
        <div className="grid gap-4 md:grid-cols-2">
          <div className="rounded-2xl border border-emerald-200 bg-emerald-50/70 p-4">
            <h3 className="text-xs font-bold uppercase tracking-wider text-emerald-800">
              Fortalezas
            </h3>
            <ul className="mt-2 list-disc pl-5 text-sm text-emerald-950 space-y-1">
              {rec.fortalezas.map((x, i) => (
                <li key={i}>{x}</li>
              ))}
            </ul>
          </div>
          <div className="rounded-2xl border border-amber-200 bg-amber-50/70 p-4">
            <h3 className="text-xs font-bold uppercase tracking-wider text-amber-800">
              Debilidades / Brechas
            </h3>
            <ul className="mt-2 list-disc pl-5 text-sm text-amber-950 space-y-1">
              {rec.debilidades.map((x, i) => (
                <li key={i}>{x}</li>
              ))}
            </ul>
          </div>
        </div>

        <div className="grid gap-4 md:grid-cols-3">
          {[
            { title: 'Mejoras Técnicas', items: rec.mejoras_tecnicas },
            { title: 'Mejoras Conceptuales', items: rec.mejoras_conceptuales },
            { title: 'Mejoras Metodológicas', items: rec.mejoras_metodologicas },
          ].map((col) => (
            <div key={col.title} className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700">
                {col.title}
              </h3>
              <ul className="mt-2 list-disc pl-4 text-xs text-slate-700 space-y-1.5">
                {col.items.map((x, i) => (
                  <li key={i}>{x}</li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
