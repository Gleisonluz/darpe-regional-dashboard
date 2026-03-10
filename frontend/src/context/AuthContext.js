import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import axios from 'axios';

const API_URL = process.env.REACT_APP_BACKEND_URL + '/api';

const AuthContext = createContext(null);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth deve ser usado dentro de um AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [token, setToken] = useState(null);
  const [isInitialized, setIsInitialized] = useState(false);

  // Inicializar token do localStorage apenas uma vez
  useEffect(() => {
    const storedToken = localStorage.getItem('darpe_token');
    if (storedToken) {
      setToken(storedToken);
    } else {
      setLoading(false);
      setIsInitialized(true);
    }
  }, []);

  // Carregar usuário quando o token estiver disponível
  const loadUser = useCallback(async (authToken) => {
    if (!authToken) {
      setLoading(false);
      setIsInitialized(true);
      return;
    }
    
    try {
      console.log('Carregando dados do usuário...');
      const response = await axios.get(`${API_URL}/auth/me`, {
        headers: { Authorization: `Bearer ${authToken}` }
      });
      console.log('Usuário carregado:', response.data.nome_completo);
      setUser(response.data);
    } catch (error) {
      console.error('Erro ao carregar usuário:', error);
      // Token inválido - limpar
      localStorage.removeItem('darpe_token');
      setToken(null);
      setUser(null);
    } finally {
      setLoading(false);
      setIsInitialized(true);
    }
  }, []);

  // Quando token muda e não é null, carregar usuário
  useEffect(() => {
    if (token && !user) {
      loadUser(token);
    }
  }, [token, user, loadUser]);

  const login = async (whatsapp, senha) => {
    try {
      console.log('Tentando login...');
      const response = await axios.post(`${API_URL}/auth/login`, { whatsapp, senha });
      const { access_token, user: userData } = response.data;
      
      console.log('Login bem-sucedido, salvando token...');
      
      // Salvar token no localStorage PRIMEIRO
      localStorage.setItem('darpe_token', access_token);
      
      // Atualizar estado - ordem importante!
      setUser(userData);
      setToken(access_token);
      
      console.log('Estado atualizado, usuário:', userData.nome_completo);
      
      return { success: true, user: userData };
    } catch (error) {
      console.error('Erro no login:', error);
      return {
        success: false,
        error: error.response?.data?.detail || 'Erro ao fazer login'
      };
    }
  };

  const register = async (userData) => {
    try {
      await axios.post(`${API_URL}/auth/register`, userData);
      return { success: true };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Erro ao registrar'
      };
    }
  };

  const logout = () => {
    console.log('Fazendo logout...');
    localStorage.removeItem('darpe_token');
    setToken(null);
    setUser(null);
  };

  const getAuthHeader = () => ({
    Authorization: `Bearer ${token}`
  });

  // isAuthenticated é true apenas quando temos user E token
  const isAuthenticated = !!user && !!token;

  // Não renderizar filhos até a inicialização completa
  if (!isInitialized) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-muted">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
          <p className="mt-4 text-slate-600">Carregando...</p>
        </div>
      </div>
    );
  }

  return (
    <AuthContext.Provider value={{ 
      user, 
      loading, 
      login, 
      logout, 
      register, 
      getAuthHeader, 
      isAuthenticated,
      token
    }}>
      {children}
    </AuthContext.Provider>
  );
};
