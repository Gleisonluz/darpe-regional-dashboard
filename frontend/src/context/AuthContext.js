import React, { createContext, useContext, useState, useEffect } from 'react';
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
  const [token, setToken] = useState(localStorage.getItem('token'));

  useEffect(() => {
    if (token) {
      loadUser();
    } else {
      setLoading(false);
    }
  }, [token]);

  const loadUser = async () => {
    try {
      const response = await axios.get(`${API_URL}/auth/me`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setUser(response.data);
    } catch (error) {
      console.error('Erro ao carregar usuário:', error);
      logout();
    } finally {
      setLoading(false);
    }
  };

  const login = async (whatsapp, senha) => {
    try {
      const response = await axios.post(`${API_URL}/auth/login`, { whatsapp, senha });
      const { access_token, user: userData } = response.data;
      setToken(access_token);
      setUser(userData);
      localStorage.setItem('token', access_token);
      return { success: true };
    } catch (error) {
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
    setToken(null);
    setUser(null);
    localStorage.removeItem('token');
  };

  const getAuthHeader = () => ({
    Authorization: `Bearer ${token}`
  });

  return (
    <AuthContext.Provider value={{ user, loading, login, logout, register, getAuthHeader, isAuthenticated: !!user }}>
      {children}
    </AuthContext.Provider>
  );
};
