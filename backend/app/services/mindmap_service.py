"""Servicio de generación y consulta del Mapa Mental Interactivo sin solapamiento de nodos."""

import json
from typing import Any

from sqlmodel import Session, select

from app.db.models import Activity, Evaluation, Submission, TopicEdge, TopicNode


X_STEP = 360.0
Y_STEP = 128.0


def _compute_horizontal_tree_layout(
    visible_nodes: list[dict[str, Any]],
    all_edges: list[TopicEdge],
) -> None:
    """
    Calcula coordenadas (x, y) de árbol horizontal (Izquierda -> Derecha) garantizando
    cero solapamiento incluso cuando se filtran nodos o ramas.
    """
    by_id = {n["id"]: n for n in visible_nodes}
    children_map: dict[str, list[str]] = {n["id"]: [] for n in visible_nodes}
    has_parent: set[str] = set()

    # Usamos únicamente aristas jerárquicas (evitando bucles con transversales 'sub-*' -> 'sub-*')
    for e in all_edges:
        if e.source_key in by_id and e.target_key in by_id:
            if e.source_key.startswith("sub-") and e.target_key.startswith("sub-"):
                continue
            if e.target_key not in children_map[e.source_key]:
                children_map[e.source_key].append(e.target_key)
                has_parent.add(e.target_key)

    roots = ["root"] if "root" in by_id else [nid for nid in by_id if nid not in has_parent]
    if not roots and visible_nodes:
        roots = [visible_nodes[0]["id"]]

    visited: set[str] = set()
    next_row = 0

    def place(node_id: str, depth: int) -> float:
        nonlocal next_row
        if node_id in visited:
            return by_id[node_id]["position"]["y"]
        visited.add(node_id)

        kids = [k for k in children_map.get(node_id, []) if k not in visited]
        if not kids:
            y = next_row * Y_STEP
            next_row += 1
        else:
            child_ys = [place(k, depth + 1) for k in kids]
            y = sum(child_ys) / len(child_ys)

        by_id[node_id]["position"] = {"x": round(depth * X_STEP, 1), "y": round(y, 1)}
        return y

    for r in roots:
        place(r, 0)

    # Cualquier nodo restante desconectado tras filtros
    for n in visible_nodes:
        if n["id"] not in visited:
            depth = {"Núcleo": 0, "Macro-Área": 1, "Eje Temático": 2}.get(
                n["data"]["category"], 3
            )
            n["position"] = {"x": round(depth * X_STEP, 1), "y": round(next_row * Y_STEP, 1)}
            next_row += 1


def build_mindmap_graph(
    session: Session,
    cohort_filter: str | None = None,
    level_filter: str | None = None,
    activity_filter: str | None = None,
) -> dict[str, Any]:
    """Retorna nodos y aristas listos para @xyflow/react con layout horizontal organizado."""
    nodes = session.exec(select(TopicNode).order_by(TopicNode.id)).all()
    edges = session.exec(select(TopicEdge).order_by(TopicEdge.id)).all()
    activities = {a.slug: a for a in session.exec(select(Activity)).all()}

    slug_scores: dict[str, float] = {}
    for slug, act in activities.items():
        sub = session.exec(
            select(Submission).where(Submission.activity_id == act.id).order_by(Submission.id.desc())
        ).first()
        if sub:
            ev = session.exec(
                select(Evaluation).where(Evaluation.submission_id == sub.id).order_by(Evaluation.id.desc())
            ).first()
            if ev:
                slug_scores[slug] = (
                    ev.final_score_approved
                    if ev.final_score_approved is not None
                    else ev.calculated_score_ai
                )

    c1_slugs = {"lab1-historia-ia", "lab2-mzles-resiliente", "lab3-vibecode", "primer-parcial"}
    c2_slugs = {"coloquio-investigaciones", "lab6-harness-organizador"}

    out_nodes: list[dict[str, Any]] = []
    visible_keys: set[str] = set()

    for n in nodes:
        slugs = json.loads(n.related_activity_slugs_json)
        matched_scores = [slug_scores[s] for s in slugs if s in slug_scores]
        if matched_scores:
            score = round(sum(matched_scores) / len(matched_scores), 2)
            level = (
                "avanzado"
                if score >= 4.2
                else ("intermedio" if score >= 3.4 else ("inicial" if score >= 2.5 else "por_profundizar"))
            )
        else:
            score = n.mastery_score
            level = n.mastery_level

        if n.node_key != "root":
            if cohort_filter:
                target = c1_slugs if cohort_filter == "C1" else c2_slugs
                if not any(s in target for s in slugs):
                    continue
            if activity_filter and activity_filter not in slugs:
                continue
            if level_filter and level != level_filter:
                continue

        visible_keys.add(n.node_key)
        out_nodes.append(
            {
                "id": n.node_key,
                "position": {"x": 0.0, "y": 0.0},
                "data": {
                    "label": n.label,
                    "category": n.category,
                    "description": n.description,
                    "mastery_level": level,
                    "mastery_score": score,
                    "related_activities": [
                        {"slug": s, "title": activities[s].title if s in activities else s}
                        for s in slugs
                    ],
                    "evidences": json.loads(n.evidences_json),
                    "gaps_to_strengthen": json.loads(n.gaps_to_strengthen_json),
                },
            }
        )

    _compute_horizontal_tree_layout(out_nodes, list(edges))

    out_edges = [
        {
            "id": f"e-{e.source_key}-{e.target_key}",
            "source": e.source_key,
            "target": e.target_key,
            "label": e.relation_label,
        }
        for e in edges
        if e.source_key in visible_keys and e.target_key in visible_keys
    ]

    return {"nodes": out_nodes, "edges": out_edges}
