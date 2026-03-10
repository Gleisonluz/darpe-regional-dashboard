import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';

export const ProtectedRoute = ({ children, allowedFunctions }) => {
  const { user, loading, isAuthenticated, token } = useAuth();
  const location = useLocation();

  // Mostrar loading enquanto verifica autenticação
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-muted">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
          <p className="mt-4 text-slate-600">Carregando...</p>
        </div>
      </div>
    );
  }

  // Redirecionar para login se não autenticado
  if (!isAuthenticated || !user || !token) {
    console.log('ProtectedRoute: Usuário não autenticado, redirecionando para login', {
      isAuthenticated,
      hasUser: !!user,
      hasToken: !!token
    });
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // Verificar permissões se allowedFunctions foi especificado
  if (allowedFunctions && allowedFunctions.length > 0) {
    const userFunctions = user.funcoes_darpe || [];
    const hasPermission = allowedFunctions.some(f => userFunctions.includes(f));
    
    if (!hasPermission) {
      console.log('ProtectedRoute: Usuário sem permissão', { userFunctions, allowedFunctions });
      return (
        <div className="min-h-screen flex items-center justify-center bg-muted p-4">
          <div className="bg-white p-8 rounded-xl shadow-lg text-center max-w-md">
            <h2 className="text-2xl font-bold text-slate-800 mb-2">Acesso Negado</h2>
            <p className="text-slate-600">Você não tem permissão para acessar esta página.</p>
          </div>
        </div>
      );
    }
  }

  console.log('ProtectedRoute: Acesso permitido para', user.nome_completo);
  return children;
};
