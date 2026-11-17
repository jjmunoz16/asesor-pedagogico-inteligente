import { useCallback, useEffect, useMemo, useState } from 'react';
import {
  Background,
  Controls,
  MiniMap,
  Position,
  ReactFlow,
  type Edge,
  type Node,
} from '@xyflow/react';
import { Download, GitBranch, Layers, Maximize2 } from 'lucide-react';
import { apiRequest } from '../api/client';
import { useAuth } from '../auth/AuthContext';
import type { ActivityItem, MindMapGraph, MindMapNodeData } from '../types';

const LEVEL_STYLES: Record<string, { border: string; bg: string; badge: string }> = {
  avanzado: { border: '#16a34a', bg: '#f0fdf4', badge: 'bg-emerald-100 text-emerald-800' },
  intermedio: { border: '#2563eb', bg: '#eff6ff', badge: 'bg-sky-100 text-sky-800' },
  inicial: { border: '#d97706', bg: '#fffbeb', badge: 'bg-amber-100 text-amber-800' },
  por_profundizar: { border: '#dc2626', bg: '#fef2f2', badge: 'bg-red-100 text-red-800' },
};

const CATEGORY_COLORS: Record<string, string> = {
  Núcleo: '#4338ca',
  'Macro-Área': '#0f172a',
  'Eje Temático': '#0369a1',
  Subtema: '#475569',
};

function escapeXml(str: string): string {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

export function MindMapPage() {
  const { token } = useAuth();
  const [graph, setGraph] = useState<MindMapGraph | null>(null);
  const [activities, setActivities] = useState<ActivityItem[]>([]);
  const [cohortFilter, setCohortFilter] = useState<string>('');
  const [activityFilter, setActivityFilter] = useState<string>('');
  const [levelFilter, setLevelFilter] = useState<string>('');
  const [showSubtopics, setShowSubtopics] = useState<boolean>(true);
  const [showCrossLinks, setShowCrossLinks] = useState<boolean>(true);
  const [search, setSearch] = useState('');
  const [selectedNode, setSelectedNode] = useState<MindMapNodeData | null>(null);

  useEffect(() => {
    apiRequest<ActivityItem[]>('/portfolio/activities', {}, token)
      .then(setActivities)
      .catch(() => {});
  }, [token]);

  useEffect(() => {
    const params = new URLSearchParams();
    if (cohortFilter) params.set('cohort', cohortFilter);
    if (levelFilter) params.set('level', levelFilter);
    if (activityFilter) params.set('activity', activityFilter);
    const qs = params.toString() ? `?${params.toString()}` : '';
    apiRequest<MindMapGraph>(`/mindmap${qs}`, {}, token).then((res) => {
      setGraph(res);
      if (res.nodes.length > 0 && !selectedNode) {
        setSelectedNode(res.nodes[0].data);
      }
    });
  }, [token, cohortFilter, levelFilter, activityFilter]);

  const onNodeClick = useCallback(
    (_: React.MouseEvent, node: Node) => {
      const raw = graph?.nodes.find((n) => n.id === node.id)?.data;
      if (raw) setSelectedNode(raw);
    },
    [graph],
  );

  const { visibleNodes, visibleEdges, rawFilteredNodes, rawFilteredEdges } = useMemo(() => {
    const rawNodes = (graph?.nodes || []).filter((n) => {
      if (!showSubtopics && n.data.category === 'Subtema') return false;
      if (
        search &&
        !n.data.label.toLowerCase().includes(search.toLowerCase()) &&
        !n.data.description.toLowerCase().includes(search.toLowerCase())
      ) {
        return false;
      }
      return true;
    });

    const idSet = new Set(rawNodes.map((n) => n.id));
    const rawEdges = (graph?.edges || []).filter((e) => {
      if (!idSet.has(e.source) || !idSet.has(e.target)) return false;
      const isCross = e.source.startsWith('sub-') && e.target.startsWith('sub-');
      if (!showCrossLinks && isCross) return false;
      return true;
    });

    // Si estamos en vista resumida (sin subtemas) recompactamos las Y para que quede equilibrado
    const positionedNodes = rawNodes.map((n) => ({ ...n, position: { ...n.position } }));
    if (!showSubtopics) {
      const byDepth: Record<number, typeof positionedNodes> = { 0: [], 1: [], 2: [] };
      positionedNodes.forEach((n) => {
        const d = n.data.category === 'Núcleo' ? 0 : n.data.category === 'Macro-Área' ? 1 : 2;
        byDepth[d].push(n);
      });
      [0, 1, 2].forEach((d) => {
        byDepth[d].forEach((n, idx) => {
          n.position = {
            x: d * 360,
            y: d === 0 ? 380 : d === 1 ? idx * 230 + 60 : idx * 125,
          };
        });
      });
    }

    const rfNodes: Node[] = positionedNodes.map((n) => {
      const styleCfg = LEVEL_STYLES[n.data.mastery_level] || LEVEL_STYLES.intermedio;
      const isRoot = n.data.category === 'Núcleo';
      const isMacro = n.data.category === 'Macro-Área';
      return {
        id: n.id,
        position: n.position,
        sourcePosition: Position.Right,
        targetPosition: Position.Left,
        data: {
          ...n.data,
          label: (
            <div className="text-left leading-snug">
              <div className="flex items-center justify-between gap-1 text-[10px] font-bold uppercase tracking-wider">
                <span style={{ color: CATEGORY_COLORS[n.data.category] || '#334155' }}>
                  {n.data.category}
                </span>
                {n.data.mastery_score > 0 && (
                  <span className="rounded-md bg-white/95 px-1.5 py-0.5 text-[10px] font-extrabold text-slate-800 shadow-2xs">
                    {n.data.mastery_score.toFixed(2)}
                  </span>
                )}
              </div>
              <div className="mt-1 font-bold text-slate-900 text-xs">{n.data.label}</div>
              <div className="mt-1 text-[10px] text-slate-500">
                {n.data.related_activities.length} act. · {n.data.evidences.length} evid.
              </div>
            </div>
          ),
        },
        style: {
          border: `${isRoot ? 3 : 2}px solid ${isRoot ? '#4338ca' : styleCfg.border}`,
          background: isRoot ? '#eef2ff' : isMacro ? '#f8fafc' : styleCfg.bg,
          borderRadius: 12,
          padding: 10,
          width: isRoot ? 265 : isMacro ? 245 : 240,
          boxShadow: '0 3px 10px rgba(15,23,42,0.06)',
        },
      };
    });

    const rfEdges: Edge[] = rawEdges.map((e) => {
      const isCross = e.source.startsWith('sub-') && e.target.startsWith('sub-');
      return {
        id: e.id,
        source: e.source,
        target: e.target,
        label: e.label,
        type: isCross ? 'smoothstep' : 'default',
        animated: isCross,
        style: {
          stroke: isCross ? '#6366f1' : '#94a3b8',
          strokeWidth: isCross ? 1.8 : 1.6,
          strokeDasharray: isCross ? '5 4' : undefined,
        },
        labelStyle: { fontSize: 10, fill: '#475569', fontWeight: 600 },
      };
    });

    return {
      visibleNodes: rfNodes,
      visibleEdges: rfEdges,
      rawFilteredNodes: positionedNodes,
      rawFilteredEdges: rawEdges,
    };
  }, [graph, showSubtopics, showCrossLinks, search]);

  function buildSvgString(): string {
    if (!rawFilteredNodes.length) return '<svg xmlns="http://www.w3.org/2000/svg"></svg>';
    const minX = Math.min(...rawFilteredNodes.map((n) => n.position.x)) - 40;
    const minY = Math.min(...rawFilteredNodes.map((n) => n.position.y)) - 40;
    const maxX = Math.max(...rawFilteredNodes.map((n) => n.position.x + 280)) + 40;
    const maxY = Math.max(...rawFilteredNodes.map((n) => n.position.y + 110)) + 40;
    const width = Math.max(900, maxX - minX);
    const height = Math.max(600, maxY - minY);
    const byId = new Map(rawFilteredNodes.map((n) => [n.id, n]));

    const edgeLines = rawFilteredEdges
      .map((e) => {
        const s = byId.get(e.source);
        const t = byId.get(e.target);
        if (!s || !t) return '';
        const x1 = s.position.x - minX + 240;
        const y1 = s.position.y - minY + 42;
        const x2 = t.position.x - minX;
        const y2 = t.position.y - minY + 42;
        const cx = (x1 + x2) / 2;
        const my = (y1 + y2) / 2 - 4;
        return `<path d="M ${x1} ${y1} C ${cx} ${y1}, ${cx} ${y2}, ${x2} ${y2}" fill="none" stroke="#94a3b8" stroke-width="1.6"/>
          <text x="${cx}" y="${my}" font-family="sans-serif" font-size="9" fill="#475569" text-anchor="middle">${escapeXml(e.label)}</text>`;
      })
      .join('');

    const nodeRects = rawFilteredNodes
      .map((n) => {
        const st = LEVEL_STYLES[n.data.mastery_level] || LEVEL_STYLES.intermedio;
        const x = n.position.x - minX;
        const y = n.position.y - minY;
        return `<g transform="translate(${x},${y})">
          <rect width="240" height="84" rx="10" fill="${st.bg}" stroke="${st.border}" stroke-width="2"/>
          <text x="10" y="18" font-family="sans-serif" font-size="9" font-weight="bold" fill="#475569">${escapeXml(n.data.category)} · ${n.data.mastery_score.toFixed(2)}</text>
          <text x="10" y="38" font-family="sans-serif" font-size="11" font-weight="bold" fill="#0f172a">${escapeXml(n.data.label.slice(0, 34))}</text>
          <text x="10" y="56" font-family="sans-serif" font-size="10" fill="#334155">${escapeXml(n.data.label.slice(34, 68))}</text>
        </g>`;
      })
      .join('');

    return `<svg xmlns="http://www.w3.org/2000/svg" width="${width}" height="${height}" style="background:#f8fafc">${edgeLines}${nodeRects}</svg>`;
  }

  function downloadJson() {
    if (!graph) return;
    const blob = new Blob([JSON.stringify(graph, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'mapa_mental_competencias_ia.json';
    a.click();
    URL.revokeObjectURL(url);
  }

  function downloadSvg() {
    const svgDoc = buildSvgString();
    const blob = new Blob([svgDoc], { type: 'image/svg+xml;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'mapa_mental_competencias_ia.svg';
    a.click();
    URL.revokeObjectURL(url);
  }

  function downloadPng() {
    const svgDoc = buildSvgString();
    const svgBlob = new Blob([svgDoc], { type: 'image/svg+xml;charset=utf-8' });
    const url = URL.createObjectURL(svgBlob);
    const img = new Image();
    img.onload = () => {
      const canvas = document.createElement('canvas');
      canvas.width = img.width;
      canvas.height = img.height;
      const ctx = canvas.getContext('2d');
      if (ctx) {
        ctx.fillStyle = '#f8fafc';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        ctx.drawImage(img, 0, 0);
        const pngUrl = canvas.toDataURL('image/png');
        const a = document.createElement('a');
        a.href = pngUrl;
        a.download = 'mapa_mental_competencias_ia.png';
        a.click();
      }
      URL.revokeObjectURL(url);
    };
    img.src = url;
  }

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-extrabold tracking-tight text-slate-900">
            Mapa Mental Interactivo de Competencias en IA
          </h1>
          <p className="text-sm text-slate-600">
            Árbol organizado de izquierda a derecha ({visibleNodes.length} nodos ·{' '}
            {visibleEdges.length} relaciones). Haz clic en cualquier nodo para ver sus evidencias.
          </p>
        </div>

        <div className="flex flex-wrap gap-2">
          <button
            onClick={() => setShowSubtopics((v) => !v)}
            className="inline-flex items-center gap-1.5 rounded-xl border border-indigo-200 bg-indigo-50 px-3 py-1.5 text-xs font-semibold text-indigo-700 hover:bg-indigo-100"
          >
            {showSubtopics ? (
              <Layers className="h-3.5 w-3.5" />
            ) : (
              <Maximize2 className="h-3.5 w-3.5" />
            )}
            {showSubtopics ? 'Vista resumida (Ejes)' : 'Vista extensa (33 nodos)'}
          </button>
          <button
            onClick={() => setShowCrossLinks((v) => !v)}
            className="inline-flex items-center gap-1.5 rounded-xl border border-slate-200 bg-white px-3 py-1.5 text-xs font-semibold text-slate-700 hover:bg-slate-50"
          >
            <GitBranch className="h-3.5 w-3.5" />
            {showCrossLinks ? 'Ocultar cruces' : 'Mostrar cruces'}
          </button>
          <button
            onClick={downloadSvg}
            className="inline-flex items-center gap-1.5 rounded-xl border border-slate-200 bg-white px-3 py-1.5 text-xs font-semibold text-slate-700 hover:bg-slate-50"
          >
            <Download className="h-3.5 w-3.5" /> SVG
          </button>
          <button
            onClick={downloadPng}
            className="inline-flex items-center gap-1.5 rounded-xl border border-slate-200 bg-white px-3 py-1.5 text-xs font-semibold text-slate-700 hover:bg-slate-50"
          >
            <Download className="h-3.5 w-3.5" /> PNG
          </button>
          <button
            onClick={downloadJson}
            className="inline-flex items-center gap-1.5 rounded-xl bg-slate-900 px-3 py-1.5 text-xs font-semibold text-white hover:bg-slate-800"
          >
            <Download className="h-3.5 w-3.5" /> JSON
          </button>
        </div>
      </div>

      <div className="flex flex-wrap gap-3 rounded-2xl border border-slate-200 bg-white p-3.5 shadow-xs">
        <select
          value={cohortFilter}
          onChange={(e) => setCohortFilter(e.target.value)}
          className="rounded-xl border border-slate-300 px-3 py-1.5 text-xs font-medium"
        >
          <option value="">Todas las cohortes</option>
          <option value="C1">Cohorte 1 — Primer Corte</option>
          <option value="C2">Cohorte 2 — Segundo Corte</option>
        </select>
        <select
          value={activityFilter}
          onChange={(e) => setActivityFilter(e.target.value)}
          className="max-w-xs rounded-xl border border-slate-300 px-3 py-1.5 text-xs font-medium"
        >
          <option value="">Todas las actividades (6)</option>
          {activities.map((a) => (
            <option key={a.slug} value={a.slug}>
              {a.cohort_code} · {a.title}
            </option>
          ))}
        </select>
        <select
          value={levelFilter}
          onChange={(e) => setLevelFilter(e.target.value)}
          className="rounded-xl border border-slate-300 px-3 py-1.5 text-xs font-medium"
        >
          <option value="">Todos los niveles</option>
          <option value="avanzado">Avanzado (≥ 4.2)</option>
          <option value="intermedio">Intermedio (3.4–4.19)</option>
          <option value="inicial">Inicial (2.5–3.39)</option>
          <option value="por_profundizar">Por profundizar (&lt; 2.5)</option>
        </select>
        <input
          type="search"
          placeholder="Buscar concepto, tecnología o herramienta..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="min-w-[230px] flex-1 rounded-xl border border-slate-300 px-3 py-1.5 text-xs"
        />
      </div>

      <div className="grid gap-4 lg:grid-cols-3">
        <div className="lg:col-span-2 h-[680px] rounded-2xl border border-slate-200 bg-white overflow-hidden shadow-xs">
          <ReactFlow
            nodes={visibleNodes}
            edges={visibleEdges}
            onNodeClick={onNodeClick}
            fitView
            minZoom={0.15}
            maxZoom={1.6}
          >
            <MiniMap zoomable pannable />
            <Controls />
            <Background gap={20} size={1} />
          </ReactFlow>
        </div>

        <aside className="rounded-2xl border border-slate-200 bg-white p-5 space-y-4 overflow-y-auto max-h-[680px] shadow-xs">
          {selectedNode ? (
            <>
              <div>
                <span className="text-xs font-bold uppercase tracking-wider text-indigo-600">
                  {selectedNode.category}
                </span>
                <h2 className="mt-1 text-lg font-bold text-slate-900">{selectedNode.label}</h2>
                <div className="mt-2 flex items-center gap-2">
                  <span
                    className={`rounded-full px-2.5 py-0.5 text-xs font-semibold ${
                      (LEVEL_STYLES[selectedNode.mastery_level] || LEVEL_STYLES.intermedio).badge
                    }`}
                  >
                    Dominio: {selectedNode.mastery_level}
                  </span>
                  {selectedNode.mastery_score > 0 && (
                    <span className="text-xs font-extrabold text-slate-800">
                      {selectedNode.mastery_score.toFixed(2)} / 5.00
                    </span>
                  )}
                </div>
              </div>

              <p className="text-sm leading-relaxed text-slate-600">{selectedNode.description}</p>

              <div>
                <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500">
                  Actividades donde se aplicó ({selectedNode.related_activities.length})
                </h3>
                <ul className="mt-1.5 space-y-1 text-xs text-slate-700">
                  {selectedNode.related_activities.map((a) => (
                    <li key={a.slug} className="rounded-lg bg-slate-50 px-3 py-1.5 font-medium">
                      • {a.title}
                    </li>
                  ))}
                </ul>
              </div>

              <div>
                <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500">
                  Evidencias reales vinculadas ({selectedNode.evidences.length})
                </h3>
                <ul className="mt-1.5 list-disc pl-4 text-xs text-slate-700 space-y-1">
                  {selectedNode.evidences.map((ev, i) => (
                    <li key={i}>{ev}</li>
                  ))}
                </ul>
              </div>

              <div>
                <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500">
                  Aspectos que requieren profundización
                </h3>
                <ul className="mt-1.5 list-disc pl-4 text-xs text-amber-800 space-y-1">
                  {selectedNode.gaps_to_strengthen.map((g, i) => (
                    <li key={i}>{g}</li>
                  ))}
                </ul>
              </div>
            </>
          ) : (
            <p className="text-sm text-slate-500">
              Selecciona cualquier nodo del mapa para ver actividades, evidencias y brechas.
            </p>
          )}
        </aside>
      </div>
    </div>
  );
}
