const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api/v1';
export const DEMO_ROLE_KEY = 'asesor_demo_role';

export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

function buildAuthHeaders(
  token?: string | null,
  initial?: HeadersInit,
  isFormData = false,
): Headers {
  const headers = new Headers(initial || {});
  if (!isFormData && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json');
  }
  if (token) {
    headers.set('Authorization', `Bearer ${token}`);
  } else {
    const demoRole = sessionStorage.getItem(DEMO_ROLE_KEY);
    if (demoRole) headers.set('X-Demo-Role', demoRole);
  }
  return headers;
}

export async function apiRequest<T>(
  path: string,
  options: RequestInit = {},
  token?: string | null,
): Promise<T> {
  const headers = buildAuthHeaders(
    token,
    options.headers,
    options.body instanceof FormData,
  );

  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    let detail = `Error HTTP ${response.status}`;
    try {
      const errBody = await response.json();
      detail = errBody.detail || JSON.stringify(errBody);
    } catch {
      // mantener mensaje por defecto
    }
    throw new ApiError(response.status, detail);
  }

  const contentType = response.headers.get('content-type') || '';
  if (contentType.includes('application/json')) {
    return (await response.json()) as T;
  }
  return (await response.text()) as unknown as T;
}

export async function apiDownloadBlob(
  path: string,
  fallbackFilename: string,
  token?: string | null,
): Promise<void> {
  const headers = buildAuthHeaders(token, undefined, true);
  const response = await fetch(`${API_BASE}${path}`, { headers });
  if (!response.ok) {
    let detail = `Error descargando archivo (HTTP ${response.status})`;
    try {
      const errBody = await response.json();
      detail = errBody.detail || detail;
    } catch {
      // mantener mensaje por defecto
    }
    throw new ApiError(response.status, detail);
  }
  const blob = await response.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = fallbackFilename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}
