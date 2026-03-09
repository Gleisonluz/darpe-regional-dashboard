import React, { useState, useEffect } from 'react';
import { useAuth } from '@/context/AuthContext';
import { Sidebar } from '@/components/Sidebar';
import { TopBar } from '@/components/TopBar';
import { Users, Church, ClipboardList, Calendar, TrendingUp } from 'lucide-react';
import { usersApi, unitsApi, attendanceApi, reportsApi } from '@/utils/api';

const DashboardPage = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState({
    totalUsers: 0,
    totalUnits: 0,
    myAttendances: 0,
    nextEvents: []
  });
  const [loading, setLoading] = useState(true);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    setLoading(true);
    try {
      const [unitsRes, agendaRes] = await Promise.all([
        unitsApi.getAll(),
        reportsApi.agenda()
      ]);

      const newStats = {
        totalUnits: unitsRes.data.length,
        nextEvents: agendaRes.data.data.slice(0, 5)
      };

      // Se for atendente, buscar suas presenças
      if (user.role === 'atendente') {
        const attendanceRes = await attendanceApi.getMyRecords();
        newStats.myAttendances = attendanceRes.data.length;
      }

      // Se for admin, buscar total de usuários
      if (['secretario_regional', 'anciao_coordenador', 'secretario_local'].includes(user.role)) {
        const usersRes = await usersApi.getAll();
        newStats.totalUsers = usersRes.data.length;
      }

      setStats(newStats);
    } catch (error) {
      console.error('Erro ao carregar dados do dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  const getRoleTitle = (role) => {
    const titles = {
      secretario_regional: 'Secretário Regional',
      anciao_coordenador: 'Ancião Coordenador',
      secretario_local: 'Secretário Local',
      atendente: 'Atendente',
      consulta: 'Consulta'
    };
    return titles[role] || role;
  };

  return (
    <div className="flex min-h-screen bg-muted">
      <Sidebar />
      
      {/* Mobile Menu Overlay */}
      {mobileMenuOpen && (
        <div className="fixed inset-0 bg-slate-900/50 z-50 md:hidden" onClick={() => setMobileMenuOpen(false)}>
          <div className="bg-white w-64 h-full" onClick={(e) => e.stopPropagation()}>
            <Sidebar />
          </div>
        </div>
      )}

      <div className="flex-1 flex flex-col min-w-0">
        <TopBar onMenuClick={() => setMobileMenuOpen(!mobileMenuOpen)} />

        <main className="flex-1 p-4 md:p-8">
          <div className="max-w-7xl mx-auto">
            {/* Cabeçalho */}
            <div className="mb-8">
              <h1 className="text-3xl md:text-4xl font-heading font-bold text-slate-900 mb-2">
                Olá, {user?.nome_completo?.split(' ')[0]}!
              </h1>
              <p className="text-lg text-slate-600">
                {getRoleTitle(user?.role)} - DARPE Regional Itajaí
              </p>
            </div>

            {loading ? (
              <div className="text-center py-12">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
                <p className="mt-4 text-slate-600">Carregando dados...</p>
              </div>
            ) : (
              <div className="space-y-8">
                {/* Cards de Estatísticas */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  {['secretario_regional', 'anciao_coordenador', 'secretario_local'].includes(user?.role) && (
                    <div data-testid="stat-card-users" className="bg-white border border-slate-100 rounded-xl p-6 shadow-sm hover:shadow-md transition-shadow">
                      <div className="flex items-center justify-between mb-4">
                        <div className="w-12 h-12 bg-accent/10 rounded-full flex items-center justify-center">
                          <Users className="w-6 h-6 text-accent" />
                        </div>
                      </div>
                      <p className="text-sm text-slate-600 mb-1">Total de Colaboradores</p>
                      <p className="text-3xl font-heading font-bold text-slate-900">{stats.totalUsers}</p>
                    </div>
                  )}

                  <div data-testid="stat-card-units" className="bg-white border border-slate-100 rounded-xl p-6 shadow-sm hover:shadow-md transition-shadow">
                    <div className="flex items-center justify-between mb-4">
                      <div className="w-12 h-12 bg-accent/10 rounded-full flex items-center justify-center">
                        <Church className="w-6 h-6 text-accent" />
                      </div>
                    </div>
                    <p className="text-sm text-slate-600 mb-1">Unidades Ativas</p>
                    <p className="text-3xl font-heading font-bold text-slate-900">{stats.totalUnits}</p>
                  </div>

                  {user?.role === 'atendente' && (
                    <div data-testid="stat-card-attendances" className="bg-white border border-slate-100 rounded-xl p-6 shadow-sm hover:shadow-md transition-shadow">
                      <div className="flex items-center justify-between mb-4">
                        <div className="w-12 h-12 bg-accent/10 rounded-full flex items-center justify-center">
                          <ClipboardList className="w-6 h-6 text-accent" />
                        </div>
                      </div>
                      <p className="text-sm text-slate-600 mb-1">Minhas Presenças</p>
                      <p className="text-3xl font-heading font-bold text-slate-900">{stats.myAttendances}</p>
                    </div>
                  )}
                </div>

                {/* Próximos Eventos */}
                <div className="bg-white border border-slate-100 rounded-xl p-6 shadow-sm">
                  <div className="flex items-center gap-3 mb-6">
                    <div className="w-10 h-10 bg-accent/10 rounded-lg flex items-center justify-center">
                      <Calendar className="w-5 h-5 text-accent" />
                    </div>
                    <h2 className="text-xl font-heading font-semibold text-slate-900">Próximas Reuniões</h2>
                  </div>

                  {stats.nextEvents.length === 0 ? (
                    <p className="text-slate-600 text-center py-8">Nenhuma reunião agendada</p>
                  ) : (
                    <div className="space-y-3">
                      {stats.nextEvents.map((event) => (
                        <div
                          key={event.id}
                          data-testid={`event-card-${event.id}`}
                          className="flex items-center justify-between p-4 bg-slate-50 rounded-lg hover:bg-slate-100 transition-colors"
                        >
                          <div className="flex-1">
                            <p className="font-medium text-slate-900">{event.nome}</p>
                            <p className="text-sm text-slate-600">{event.cidade}</p>
                          </div>
                          <div className="text-right">
                            <p className="text-sm font-medium text-slate-900 capitalize">{event.dia_semana}</p>
                            <p className="text-sm text-slate-600">{event.horario}</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </main>
      </div>
    </div>
  );
};

export default DashboardPage;
