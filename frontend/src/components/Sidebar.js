import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import {
  Home,
  Church,
  Users,
  ClipboardList,
  FileText,
  CreditCard,
  Bell,
  LogOut,
  BarChart3,
  Calendar
} from 'lucide-react';
import { Button } from '@/components/ui/button';

export const Sidebar = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const hasFunction = (func) => {
    return user?.funcoes_darpe?.includes(func);
  };

  const isAdmin = () => {
    return hasFunction('Secretário Regional') || hasFunction('Ancião Coordenador');
  };

  const navItems = [
    { to: '/dashboard', icon: Home, label: 'Início', show: true },
    { to: '/credential', icon: CreditCard, label: 'Credencial', show: hasFunction('Atendente') },
    { to: '/attendance', icon: ClipboardList, label: 'Registrar Presença', show: hasFunction('Atendente') },
    { to: '/service', icon: FileText, label: 'Registrar Atendimento', show: hasFunction('Atendente') || hasFunction('Secretário Local') || isAdmin() },
    { to: '/units', icon: Church, label: 'Unidades', show: hasFunction('Secretário Local') || isAdmin() },
    { to: '/users', icon: Users, label: 'Colaboradores', show: hasFunction('Secretário Local') || isAdmin() },
    { to: '/agenda', icon: Calendar, label: 'Agenda', show: true },
    { to: '/reports', icon: BarChart3, label: 'Relatórios', show: hasFunction('Secretário Local') || isAdmin() },
  ];

  const filteredNavItems = navItems.filter(item => item.show);

  return (
    <aside className="hidden md:flex md:flex-col w-64 bg-white border-r border-slate-200 min-h-screen">
      <div className="p-6 border-b border-slate-100">
        <h1 className="text-xl font-heading font-bold text-primary">DARPE Regional</h1>
        <p className="text-sm text-slate-500">Itajaí</p>
      </div>

      <nav className="flex-1 p-4 space-y-1">
        {filteredNavItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            data-testid={`nav-${item.to.replace('/', '')}`}
            className={({ isActive }) =>
              `flex items-center gap-3 px-4 py-3 rounded-lg transition-all ${isActive
                ? 'bg-slate-100 text-slate-900 font-medium'
                : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
              }`
            }
          >
            <item.icon className="w-5 h-5" />
            <span>{item.label}</span>
          </NavLink>
        ))}
      </nav>

      <div className="p-4 border-t border-slate-100">
        <div className="flex items-center gap-3 mb-4 p-3 bg-slate-50 rounded-lg">
          <div className="w-10 h-10 rounded-full bg-accent flex items-center justify-center text-white font-semibold">
            {user?.nome_completo?.charAt(0)}
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-slate-900 truncate">{user?.nome_completo}</p>
            <p className="text-xs text-slate-500">{user?.funcoes_darpe?.join(', ')}</p>
          </div>
        </div>
        <Button
          data-testid="logout-button"
          onClick={handleLogout}
          variant="ghost"
          className="w-full justify-start text-red-600 hover:text-red-700 hover:bg-red-50"
        >
          <LogOut className="w-4 h-4 mr-2" />
          Sair
        </Button>
      </div>
    </aside>
  );
};
