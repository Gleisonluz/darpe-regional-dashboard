import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { toast } from 'sonner';

const LoginPage = () => {
  const [isLogin, setIsLogin] = useState(true);
  const [loading, setLoading] = useState(false);
  const { login, register } = useAuth();
  const navigate = useNavigate();

  const [loginData, setLoginData] = useState({ email: '', senha: '' });
  const [registerData, setRegisterData] = useState({
    email: '',
    senha: '',
    nome_completo: '',
    role: 'atendente',
    cidade: ''
  });

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    const result = await login(loginData.email, loginData.senha);
    setLoading(false);

    if (result.success) {
      toast.success('Login realizado com sucesso!');
      navigate('/dashboard');
    } else {
      toast.error(result.error);
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setLoading(true);
    const result = await register(registerData);
    setLoading(false);

    if (result.success) {
      toast.success('Registro realizado! Aguarde aprovação do administrador.');
      setIsLogin(true);
      setRegisterData({ email: '', senha: '', nome_completo: '', role: 'atendente', cidade: '' });
    } else {
      toast.error(result.error);
    }
  };

  return (
    <div className="min-h-screen flex">
      {/* Lado Esquerdo - Imagem/Info */}
      <div className="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-slate-800 to-slate-900 p-12 flex-col justify-between relative overflow-hidden">
        <div className="absolute inset-0 opacity-10">
          <div className="absolute inset-0" style={{
            backgroundImage: `url('data:image/svg+xml,%3Csvg width="60" height="60" viewBox="0 0 60 60" xmlns="http://www.w3.org/2000/svg"%3E%3Cg fill="none" fill-rule="evenodd"%3E%3Cg fill="%23ffffff" fill-opacity="0.4"%3E%3Cpath d="M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z"/%3E%3C/g%3E%3C/g%3E%3C/svg%3E')`
          }}></div>
        </div>
        <div className="relative z-10">
          <h1 className="text-4xl font-heading font-bold text-white mb-4">DARPE Regional Itajaí</h1>
          <p className="text-lg text-slate-300">Sistema de Gestão de Evangelização</p>
        </div>
        <div className="relative z-10">
          <blockquote className="text-slate-300 text-lg italic">
            "Ide por todo o mundo, pregai o evangelho a toda criatura."
          </blockquote>
          <p className="text-slate-400 mt-2">Marcos 16:15</p>
        </div>
      </div>

      {/* Lado Direito - Formulário */}
      <div className="w-full lg:w-1/2 flex items-center justify-center p-8 bg-muted">
        <div className="w-full max-w-md">
          {/* Logo para mobile */}
          <div className="lg:hidden mb-8 text-center">
            <h1 className="text-3xl font-heading font-bold text-primary mb-2">DARPE Regional</h1>
            <p className="text-slate-600">Itajaí</p>
          </div>

          <div className="bg-white rounded-xl shadow-lg p-8 border border-slate-100">
            <div className="mb-8">
              <h2 className="text-2xl font-heading font-bold text-slate-900 mb-2">
                {isLogin ? 'Bem-vindo de volta' : 'Criar conta'}
              </h2>
              <p className="text-slate-600">
                {isLogin ? 'Entre com suas credenciais' : 'Preencha seus dados para se cadastrar'}
              </p>
            </div>

            {isLogin ? (
              <form onSubmit={handleLogin} className="space-y-4">
                <div>
                  <label className="text-sm font-medium text-slate-700 mb-2 block">Email</label>
                  <Input
                    data-testid="login-email-input"
                    type="email"
                    placeholder="seu@email.com"
                    value={loginData.email}
                    onChange={(e) => setLoginData({ ...loginData, email: e.target.value })}
                    required
                  />
                </div>
                <div>
                  <label className="text-sm font-medium text-slate-700 mb-2 block">Senha</label>
                  <Input
                    data-testid="login-password-input"
                    type="password"
                    placeholder="••••••••"
                    value={loginData.senha}
                    onChange={(e) => setLoginData({ ...loginData, senha: e.target.value })}
                    required
                  />
                </div>
                <Button
                  data-testid="login-submit-button"
                  type="submit"
                  className="w-full bg-primary hover:bg-primary/90 text-white rounded-full"
                  disabled={loading}
                >
                  {loading ? 'Entrando...' : 'Entrar'}
                </Button>
              </form>
            ) : (
              <form onSubmit={handleRegister} className="space-y-4">
                <div>
                  <label className="text-sm font-medium text-slate-700 mb-2 block">Nome Completo</label>
                  <Input
                    data-testid="register-name-input"
                    type="text"
                    placeholder="Seu nome completo"
                    value={registerData.nome_completo}
                    onChange={(e) => setRegisterData({ ...registerData, nome_completo: e.target.value })}
                    required
                  />
                </div>
                <div>
                  <label className="text-sm font-medium text-slate-700 mb-2 block">Email</label>
                  <Input
                    data-testid="register-email-input"
                    type="email"
                    placeholder="seu@email.com"
                    value={registerData.email}
                    onChange={(e) => setRegisterData({ ...registerData, email: e.target.value })}
                    required
                  />
                </div>
                <div>
                  <label className="text-sm font-medium text-slate-700 mb-2 block">Cidade</label>
                  <Input
                    data-testid="register-city-input"
                    type="text"
                    placeholder="Sua cidade"
                    value={registerData.cidade}
                    onChange={(e) => setRegisterData({ ...registerData, cidade: e.target.value })}
                    required
                  />
                </div>
                <div>
                  <label className="text-sm font-medium text-slate-700 mb-2 block">Senha</label>
                  <Input
                    data-testid="register-password-input"
                    type="password"
                    placeholder="••••••••"
                    value={registerData.senha}
                    onChange={(e) => setRegisterData({ ...registerData, senha: e.target.value })}
                    required
                  />
                </div>
                <Button
                  data-testid="register-submit-button"
                  type="submit"
                  className="w-full bg-primary hover:bg-primary/90 text-white rounded-full"
                  disabled={loading}
                >
                  {loading ? 'Cadastrando...' : 'Cadastrar'}
                </Button>
              </form>
            )}

            <div className="mt-6 text-center">
              <button
                data-testid="toggle-form-button"
                onClick={() => setIsLogin(!isLogin)}
                className="text-sm text-accent hover:text-accent/80 font-medium"
              >
                {isLogin ? 'Não tem conta? Cadastre-se' : 'Já tem conta? Faça login'}
              </button>
            </div>

            <div className="mt-6 pt-6 border-t border-slate-100 text-center">
              <Link to="/" className="text-sm text-slate-600 hover:text-slate-900">
                ← Voltar para página pública
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
