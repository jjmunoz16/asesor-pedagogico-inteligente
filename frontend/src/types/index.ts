export type UserRole = 'student' | 'teacher' | 'admin';

export interface User {
  id: number;
  email: string;
  full_name: string;
  role: UserRole;
}

export interface EvidenceSummary {
  id: number;
  filename: string;
  relative_path: string;
  file_category: string;
  size_bytes: number;
  sha256_hash: string;
  extraction_status: 'extracted' | 'partial_metadata_only' | 'unsupported';
  extracted_text_summary?: string;
}

export interface ActivityItem {
  id: number;
  slug: string;
  title: string;
  activity_type: string;
  cohort_id: number;
  cohort_code: string;
  cohort_name: string;
  official_objective: string | null;
  objective_source: string | null;
  description: string;
  has_valid_rubric: boolean;
  rubric_is_template: boolean;
  rubric_version: number | null;
  latest_submission_id: number | null;
  evidence_count: number;
  evidences: EvidenceSummary[];
  latest_evaluation: {
    id: number;
    status: string;
    calculated_score_ai: number;
    final_score_approved: number | null;
    ai_provider: string;
    ai_model: string;
  } | null;
}

export interface RubricCriterionItem {
  id?: number;
  code: string;
  competency_name: string;
  criterion_name: string;
  description: string;
  weight_percent: number;
  performance_levels: Record<string, number>;
}

export interface RubricResponse {
  activity_id: number;
  rubric: {
    id: number;
    name: string;
    is_template_proposal: boolean;
    active_version: {
      id: number;
      version_number: number;
      is_valid: boolean;
      notes: string;
      created_at: string;
      total_weight: number;
      criteria: RubricCriterionItem[];
    };
    versions_history: Array<{
      id: number;
      version_number: number;
      is_valid: boolean;
      notes: string;
      created_at: string;
    }>;
  } | null;
}

export interface IndividualReport {
  evaluation_id: number;
  status: 'draft_ai' | 'under_review' | 'approved' | 'rejected';
  activity: {
    id: number;
    slug: string;
    title: string;
    cohort: string;
    cohort_code: string;
    official_objective: string | null;
    objective_source: string | null;
  };
  submission: {
    id: number;
    student_group_name: string;
    submitted_at: string;
    evidences: EvidenceSummary[];
  };
  traceability: {
    rubric_name: string;
    rubric_version: number;
    is_template_proposal: boolean;
    ai_provider: string;
    ai_model: string;
    prompt_version: string;
    created_at: string;
  };
  dimension_verificacion: {
    objetivo_cumplido: string;
    resumen_verificacion: string;
    evidencias_citadas: Array<{ archivo: string; ubicacion: string; fragmento: string }>;
    faltantes_detectados: string[];
  };
  verificacion_tecnica_sandbox: {
    executed: boolean;
    sandbox_mode: string | null;
    syntax_valid: boolean | null;
    files_checked: Array<Record<string, unknown>>;
    static_findings: string[];
    unit_tests_passed: number | null;
    unit_tests_total: number | null;
    execution_time_ms: number;
  };
  dimension_cuantificacion: {
    calculated_score_ai: number;
    final_score_approved: number | null;
    effective_final_score: number;
    criteria: Array<{
      criterion_evaluation_id: number;
      code: string;
      competency_name: string;
      criterion_name: string;
      weight_percent: number;
      ai_level_label: string;
      ai_criterion_score: number;
      teacher_criterion_score: number | null;
      effective_score: number;
      weighted_contribution: number;
      cited_evidences: string[];
      justification: string;
    }>;
  };
  dimension_recomendacion: {
    fortalezas: string[];
    debilidades: string[];
    mejoras_tecnicas: string[];
    mejoras_conceptuales: string[];
    mejoras_metodologicas: string[];
  };
  teacher_reviews: Array<{
    id: number;
    decision: string;
    comments: string;
    score_diff: Record<string, unknown>;
    reviewed_at: string;
  }>;
}

export interface IntegratedReport {
  total_activities: number;
  evaluated_activities: number;
  global_average: number | null;
  cohort_evolution: Array<{
    cohort_code: string;
    cohort_name: string;
    activities_evaluated: number;
    average_score: number | null;
  }>;
  activities: Array<{
    activity_id: number;
    slug: string;
    title: string;
    cohort_code: string;
    cohort_name: string;
    evaluation_id: number | null;
    status: string;
    score: number | null;
    objective_met: string | null;
  }>;
  competencies: Array<{
    competency: string;
    average_score: number;
    mastery_level: string;
  }>;
  identified_gaps: string[];
  strengthening_plan: string[];
}

export interface MindMapNodeData extends Record<string, unknown> {
  label: string;
  category: string;
  description: string;
  mastery_level: 'avanzado' | 'intermedio' | 'inicial' | 'por_profundizar';
  mastery_score: number;
  related_activities: Array<{ slug: string; title: string }>;
  evidences: string[];
  gaps_to_strengthen: string[];
}

export interface MindMapGraph {
  nodes: Array<{
    id: string;
    position: { x: number; y: number };
    data: MindMapNodeData;
  }>;
  edges: Array<{
    id: string;
    source: string;
    target: string;
    label: string;
  }>;
}
