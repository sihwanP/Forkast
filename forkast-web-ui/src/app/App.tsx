import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AppShell } from '../layouts/AppShell';
import { useAppStore } from '../store/useAppStore';
import * as Pages from '../pages';

const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const isAuth = useAppStore((state) => state.isAuth);
  if (!isAuth) return <Navigate to="/login" replace />;
  return <>{children}</>;
};

export const AppRouter = () => {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Pages.LoginPage />} />
        
        <Route element={<ProtectedRoute><AppShell /></ProtectedRoute>}>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<Pages.DashboardPage />} />
          <Route path="/analytics" element={<Pages.AnalyticsPage />} />
          <Route path="/forecast" element={<Pages.ForecastPage />} />
          <Route path="/menu-performance" element={<Pages.MenuPerformancePage />} />
          <Route path="/insights" element={<Pages.InsightsPage />} />
          <Route path="/delivery" element={<Pages.DeliveryPage />} />
          <Route path="/alerts" element={<Pages.AlertsPage />} />
          <Route path="/settings" element={<Pages.SettingsPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
};
