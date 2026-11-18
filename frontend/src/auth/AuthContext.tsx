import React, { createContext, useContext, useEffect, useState } from 'react';
import { apiRequest, DEMO_ROLE_KEY } from '../api/client';
import type { User, UserRole } from '../types';

interface AuthState {
  user: User | null;
  token: string | null;
  loading: boolean;
  isOpenDemo: boolean;
  demoRole: UserRole;
  switchDemoRole: (role: UserRole) => void;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, fullName: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthState | undefined>(undefined);
const TOKEN_KEY = 'asesor_jwt_token';

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [token, setToken] = useState<string | null>(() => sessionStorage.getItem(TOKEN_KEY));
  const [demoRole, setDemoRole] = useState<UserRole>(
    () => (sessionStorage.getItem(DEMO_ROLE_KEY) as UserRole) || 'teacher',
  );
  const [user, setUser] = useState<User | null>(null);
  const [isOpenDemo, setIsOpenDemo] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);

    apiRequest<{ public_demo_mode?: boolean }>('/health')
      .then((h) => {
        const openMode = h.public_demo_mode === true;
        if (!cancelled) setIsOpenDemo(openMode);
        if (!token && !openMode) {
          return null;
        }
        return apiRequest<User>('/auth/me', {}, token);
      })
      .then((u) => {
        if (!cancelled) setUser(u);
      })
      .catch(() => {
        if (!cancelled) {
          if (token) {
            sessionStorage.removeItem(TOKEN_KEY);
            setToken(null);
          }
          setUser(null);
        }
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [token, demoRole]);

  function switchDemoRole(role: UserRole) {
    sessionStorage.setItem(DEMO_ROLE_KEY, role);
    setDemoRole(role);
  }

  async function login(email: string, password: string) {
    const res = await apiRequest<{ access_token: string; user: User }>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
    sessionStorage.setItem(TOKEN_KEY, res.access_token);
    setToken(res.access_token);
    setUser(res.user);
  }

  async function register(email: string, fullName: string, password: string) {
    const res = await apiRequest<{ access_token: string; user: User }>('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ email, full_name: fullName, password }),
    });
    sessionStorage.setItem(TOKEN_KEY, res.access_token);
    setToken(res.access_token);
    setUser(res.user);
  }

  async function logout() {
    if (token) {
      await apiRequest('/auth/logout', { method: 'POST' }, token).catch(() => {});
    }
    sessionStorage.removeItem(TOKEN_KEY);
    setToken(null);
    setUser(null);
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        loading,
        isOpenDemo,
        demoRole,
        switchDemoRole,
        login,
        register,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth debe usarse dentro de AuthProvider');
  return ctx;
}
