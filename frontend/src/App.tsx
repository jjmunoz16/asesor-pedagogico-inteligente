import { Navigate, Route, Routes } from 'react-router-dom';
import { useAuth } from './auth/AuthContext';
import { Layout } from './components/Layout';
import { AdminModelsPage } from './pages/AdminModelsPage';
import { EvaluationReportPage } from './pages/EvaluationReportPage';
import { IntegratedReportPage } from './pages/IntegratedReportPage';
import { LoginPage } from './pages/LoginPage';
import { MindMapPage } from './pages/MindMapPage';
import { OverviewPage } from './pages/OverviewPage';
import { PortfolioPage } from './pages/PortfolioPage';
import { RubricsPage } from './pages/RubricsPage';
import { TeacherReviewPage } from './pages/TeacherReviewPage';

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { user, loading, isOpenDemo } = useAuth();
  if (loading) return <p className="p-6 text-sm text-slate-500">Cargando plataforma...</p>;
  if (!user && !isOpenDemo) return <Navigate to="/login" replace />;
  return <>{children}</>;
}

export function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<OverviewPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route
          path="/portafolio"
          element={
            <ProtectedRoute>
              <PortfolioPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/rubricas"
          element={
            <ProtectedRoute>
              <RubricsPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/evaluaciones/:evaluationId"
          element={
            <ProtectedRoute>
              <EvaluationReportPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/docente/revision"
          element={
            <ProtectedRoute>
              <TeacherReviewPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/informe-integral"
          element={
            <ProtectedRoute>
              <IntegratedReportPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/mapa-mental"
          element={
            <ProtectedRoute>
              <MindMapPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin/modelos"
          element={
            <ProtectedRoute>
              <AdminModelsPage />
            </ProtectedRoute>
          }
        />
      </Route>
    </Routes>
  );
}

export default App;
