import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  ArrowRight,
  CheckCircle2,
  Cpu,
  FileCheck2,
  FolderGit2,
  LineChart,
  LockOpen,
  Network,
  ShieldCheck,
} from 'lucide-react';
import { apiRequest } from '../api/client';

interface OverviewData {
  project_title: string;
  course: string;
  university: string;
  abstract: string;
  technologies: string[];
  team: Array<{ name: string; role: string; initials: string; photo_url: string | null }>;
}

export function OverviewPage() {
  const [data, setData] = useState<OverviewData | null>(null);

  useEffect(() => {
    apiRequest<OverviewData>('/public/overview').then(setData).catch(() => {});
  }, []);

  return (
    <div className="space-y-8">
      <section className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-slate-900 via-indigo-900 to-indigo-700 p-8 sm:p-10 text-white shadow-xl">
        <div className="relative z-10 max-w-4xl">
          <span className="inline-flex items-center gap-2 rounded-full border border-white/20 bg-white/10 px-3.5 py-1 text-xs font-semibold tracking-wide text-indigo-100 backdrop-blur">
            {data?.university || 'Universidad de Manizales'} · {data?.course || 'Profundización I – IA'}
          </span>
          <h1 className="mt-4 text-3xl sm:text-4xl font-extrabold tracking-tight">
            {data?.project_title || 'Asesor Pedagógico Inteligente'}
          </h1>
          <p className="mt-3 text-sm sm:text-base leading-relaxed text-indigo-100/95">
            {data?.abstract ||
              'Plataforma web inteligente para la evaluación en 3 dimensiones, verificación técnica en sandbox, supervisión docente HITL y mapa mental interactivo de competencias en IA.'}
          </p>

          <div className="mt-7 flex flex-wrap gap-3">
            <Link
              to="/portafolio"
              className="inline-flex items-center gap-2 rounded-xl bg-white px-5 py-2.5 text-sm font-bold text-indigo-900 shadow-sm transition hover:bg-indigo-50"
            >
              <FolderGit2 className="h-4 w-4" /> Explorar Portafolio
              <ArrowRight className="h-4 w-4" />
            </Link>
            <Link
              to="/informe-integral"
              className="inline-flex items-center gap-2 rounded-xl border border-white/25 bg-white/10 px-4 py-2.5 text-sm font-semibold text-white backdrop-blur transition hover:bg-white/20"
            >
              <LineChart className="h-4 w-4" /> Informe Integral
            </Link>
            <Link
              to="/mapa-mental"
              className="inline-flex items-center gap-2 rounded-xl border border-white/25 bg-white/10 px-4 py-2.5 text-sm font-semibold text-white backdrop-blur transition hover:bg-white/20"
            >
              <Network className="h-4 w-4" /> Mapa Mental Interactivo
            </Link>
          </div>
        </div>

        <div className="mt-8 grid grid-cols-2 gap-3 sm:grid-cols-4">
          {[
            { value: '6', label: 'Actividades reales' },
            { value: '2', label: 'Cohortes académicas' },
            { value: '3D', label: 'Método de evaluación' },
            { value: '33', label: 'Nodos en Mapa Mental' },
          ].map((stat) => (
            <div
              key={stat.label}
              className="rounded-2xl border border-white/15 bg-white/10 px-4 py-3 backdrop-blur"
            >
              <p className="text-2xl font-extrabold text-white">{stat.value}</p>
              <p className="text-xs text-indigo-100">{stat.label}</p>
            </div>
          ))}
        </div>
      </section>

      <div className="flex items-start gap-3 rounded-2xl border border-sky-200 bg-sky-50/80 px-5 py-4 text-xs sm:text-sm text-sky-950">
        <LockOpen className="mt-0.5 h-5 w-5 shrink-0 text-sky-600" />
        <div>
          <strong>Acceso directo habilitado para revisión docente:</strong> todas las secciones están
          abiertas sin pantalla de login para facilitar la exploración inmediata. El módulo de
          autenticación <strong>JWT + control por roles (RBAC)</strong> ya está implementado y
          probado; puede activarse en cualquier momento con <code>PUBLIC_DEMO_MODE=false</code>.
        </div>
      </div>

      <section className="grid gap-5 md:grid-cols-3">
        <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-xs transition hover:shadow-md">
          <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-indigo-50 text-indigo-600">
            <FileCheck2 className="h-6 w-6" />
          </div>
          <h2 className="mt-4 text-base font-bold text-slate-900">1. Verificación con Evidencias</h2>
          <p className="mt-1.5 text-sm leading-relaxed text-slate-600">
            Contrasta los objetivos de cada actividad contra citas reales extraídas de PDFs, informes,
            código fuente y resultados técnicos de sandbox.
          </p>
        </div>

        <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-xs transition hover:shadow-md">
          <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-emerald-50 text-emerald-600">
            <CheckCircle2 className="h-6 w-6" />
          </div>
          <h2 className="mt-4 text-base font-bold text-slate-900">2. Cuantificación Determinista</h2>
          <p className="mt-1.5 text-sm leading-relaxed text-slate-600">
            Rúbricas versionadas al 100 % y validación Pydantic estricta. El backend calcula la nota
            final (0,0–5,0), nunca el LLM.
          </p>
        </div>

        <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-xs transition hover:shadow-md">
          <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-amber-50 text-amber-600">
            <ShieldCheck className="h-6 w-6" />
          </div>
          <h2 className="mt-4 text-base font-bold text-slate-900">3. Supervisión Docente HITL</h2>
          <p className="mt-1.5 text-sm leading-relaxed text-slate-600">
            Toda evaluación inicia como borrador trazable y permite revisión en pantalla dividida,
            ajuste argumentado y aprobación docente.
          </p>
        </div>
      </section>

      <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-xs">
        <div className="flex items-center gap-2.5">
          <Cpu className="h-5 w-5 text-indigo-600" />
          <h2 className="text-lg font-bold text-slate-900">Arquitectura y Stack (100 % Gratuito)</h2>
        </div>
        <div className="mt-4 grid gap-2.5 sm:grid-cols-2">
          {(data?.technologies || []).map((tech) => (
            <div
              key={tech}
              className="flex items-center gap-2.5 rounded-xl border border-slate-100 bg-slate-50 px-3.5 py-2.5 text-sm font-medium text-slate-700"
            >
              <span className="h-2 w-2 shrink-0 rounded-full bg-indigo-500" />
              {tech}
            </div>
          ))}
        </div>
      </section>

      <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-xs">
        <h2 className="text-lg font-bold text-slate-900">Equipo Desarrollador</h2>
        <p className="mt-1 text-sm text-slate-500">
          Estudiantes de Ingeniería de Sistemas y Telecomunicaciones — Universidad de Manizales
        </p>
        <div className="mt-4 grid gap-4 sm:grid-cols-2">
          {(
            data?.team || [
              {
                name: 'Juan José Muñoz Naranjo',
                role: 'Arquitectura, Backend, Harness IA y Verificación',
                initials: 'JM',
                photo_url: null,
              },
              {
                name: 'Christopher Villa Noreña',
                role: 'Frontend React, Experiencia de Usuario y Mapa Mental Interactivo',
                initials: 'CV',
                photo_url: null,
              },
            ]
          ).map((member) => (
            <div
              key={member.name}
              className="flex items-center gap-4 rounded-2xl border border-slate-200 bg-gradient-to-r from-slate-50 to-white p-5"
            >
              {member.photo_url ? (
                <img
                  src={member.photo_url}
                  alt={member.name}
                  className="h-16 w-16 rounded-full object-cover ring-2 ring-indigo-100"
                />
              ) : (
                <div className="flex h-16 w-16 shrink-0 items-center justify-center rounded-2xl bg-gradient-to-br from-indigo-600 to-violet-600 text-lg font-bold text-white shadow-sm">
                  {member.initials}
                </div>
              )}
              <div>
                <h3 className="text-base font-bold text-slate-900">{member.name}</h3>
                <p className="mt-0.5 text-sm text-slate-600">{member.role}</p>
              </div>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
