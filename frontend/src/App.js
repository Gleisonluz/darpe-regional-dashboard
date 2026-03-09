import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from '@/context/AuthContext';
import { ProtectedRoute } from '@/components/ProtectedRoute';
import { Toaster } from 'sonner';
import '@/App.css';

// Pages
import HomePage from '@/pages/HomePage';
import LoginPage from '@/pages/LoginPage';
import DashboardPage from '@/pages/DashboardPage';
import CredentialPage from '@/pages/CredentialPage';
import AttendancePage from '@/pages/AttendancePage';
import ServicePage from '@/pages/ServicePage';
import UnitsPage from '@/pages/UnitsPage';
import UsersPage from '@/pages/UsersPage';
import AgendaPage from '@/pages/AgendaPage';
import ReportsPage from '@/pages/ReportsPage';
import NotificationsPage from '@/pages/NotificationsPage';

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Toaster position="top-right" richColors />
        <Routes>
          {/* Public Routes */}
          <Route path="/" element={<HomePage />} />
          <Route path="/login" element={<LoginPage />} />

          {/* Protected Routes */}
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <DashboardPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/credential"
            element={
              <ProtectedRoute allowedFunctions={['Atendente']}>
                <CredentialPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/attendance"
            element={
              <ProtectedRoute allowedFunctions={['Atendente']}>
                <AttendancePage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/service"
            element={
              <ProtectedRoute allowedFunctions={['Secretário Regional', 'Ancião Coordenador', 'Secretário Local', 'Atendente']}>
                <ServicePage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/units"
            element={
              <ProtectedRoute allowedFunctions={['Secretário Regional', 'Ancião Coordenador', 'Secretário Local']}>
                <UnitsPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/users"
            element={
              <ProtectedRoute allowedFunctions={['Secretário Regional', 'Ancião Coordenador', 'Secretário Local']}>
                <UsersPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/agenda"
            element={
              <ProtectedRoute>
                <AgendaPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/reports"
            element={
              <ProtectedRoute allowedFunctions={['Secretário Regional', 'Ancião Coordenador', 'Secretário Local']}>
                <ReportsPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/notifications"
            element={
              <ProtectedRoute>
                <NotificationsPage />
              </ProtectedRoute>
            }
          />

          {/* Redirect */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
