import React, { useState, useEffect } from 'react';
import { Sidebar } from '@/components/Sidebar';
import { TopBar } from '@/components/TopBar';
import { reportsApi } from '@/utils/api';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { TrendingUp, Users, MapPin, Church } from 'lucide-react';

const COLORS = ['#0EA5E9', '#334155', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899', '#06B6D4'];

const ReportsPage = () => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [loading, setLoading] = useState(true);
  const [reports, setReports] = useState({
    byCity: [],
    byUnit: [],
    activeAttendees: 0,
    inactiveAttendees: 0
  });

  useEffect(() => {
    loadReports();
  }, []);

  const loadReports = async () => {
    setLoading(true);
    try {
      const [cityRes, unitRes, activeRes, inactiveRes] = await Promise.all([
        reportsApi.attendanceByCity(),
        reportsApi.attendanceByUnit(),
        reportsApi.activeAttendees(),
        reportsApi.inactiveAttendees()
      ]);

      const cityData = cityRes.data.data.map(item => ({
        name: item._id,
        total: item.total
      }));

      const unitData = unitRes.data.data.slice(0, 10).map(item => ({
        name: item.unidade_nome,
        cidade: item.cidade,
        total: item.total
      }));

      const statusData = [
        { name: 'Ativos', value: activeRes.data.total, color: '#10B981' },
        { name: 'Inativos', value: inactiveRes.data.total, color: '#EF4444' }
      ];

      setReports({
        byCity: cityData,
        byUnit: unitData,
        activeAttendees: activeRes.data.total,
        inactiveAttendees: inactiveRes.data.total,
        statusData: statusData
      });
    } catch (error) {
      console.error('Erro ao carregar relatórios:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen bg-muted">
      <Sidebar />
      {mobileMenuOpen && (
        <div className="fixed inset-0 bg-slate-900/50 z-50 md:hidden" onClick={() => setMobileMenuOpen(false)}>
          <div className="bg-white w-64 h-full"><Sidebar /></div>
        </div>
      )}
      <div className="flex-1 flex flex-col">
        <TopBar onMenuClick={() => setMobileMenuOpen(!mobileMenuOpen)} />
        <main className="flex-1 p-4 md:p-8">
          <div className="max-w-7xl mx-auto">
            <div className="mb-8">
              <h1 className="text-3xl font-heading font-bold text-slate-900 mb-2">Relatórios e Estatísticas</h1>
              <p className="text-slate-600">Visualize dados e métricas da regional</p>
            </div>

            {loading ? (
              <div className="text-center py-12">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
                <p className="mt-4 text-slate-600">Carregando relatórios...</p>
              </div>
            ) : (
              <div className="space-y-8">
                {/* Cards de Resumo */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div className="bg-white border border-slate-100 rounded-xl p-6 shadow-sm">
                    <div className="flex items-center justify-between mb-4">
                      <div className="w-12 h-12 bg-emerald-50 rounded-lg flex items-center justify-center">
                        <Users className="w-6 h-6 text-emerald-600" />
                      </div>
                      <TrendingUp className="w-5 h-5 text-emerald-600" />
                    </div>
                    <p className="text-sm text-slate-600 mb-1">Atendentes Ativos</p>
                    <p className="text-3xl font-heading font-bold text-slate-900">{reports.activeAttendees}</p>
                  </div>

                  <div className="bg-white border border-slate-100 rounded-xl p-6 shadow-sm">
                    <div className="flex items-center justify-between mb-4">
                      <div className="w-12 h-12 bg-red-50 rounded-lg flex items-center justify-center">
                        <Users className="w-6 h-6 text-red-600" />
                      </div>
                    </div>
                    <p className="text-sm text-slate-600 mb-1">Atendentes Inativos</p>
                    <p className="text-3xl font-heading font-bold text-slate-900">{reports.inactiveAttendees}</p>
                  </div>

                  <div className="bg-white border border-slate-100 rounded-xl p-6 shadow-sm">
                    <div className="flex items-center justify-between mb-4">
                      <div className="w-12 h-12 bg-accent/10 rounded-lg flex items-center justify-center">
                        <MapPin className="w-6 h-6 text-accent" />
                      </div>
                    </div>
                    <p className="text-sm text-slate-600 mb-1">Cidades Atendidas</p>
                    <p className="text-3xl font-heading font-bold text-slate-900">{reports.byCity.length}</p>
                  </div>
                </div>

                {/* Gráfico de Presenças por Cidade */}
                {reports.byCity.length > 0 && (
                  <div className="bg-white border border-slate-100 rounded-xl p-6 shadow-sm">
                    <h2 className="text-xl font-heading font-semibold text-slate-900 mb-6">Presenças por Cidade</h2>
                    <ResponsiveContainer width="100%" height={300}>
                      <BarChart data={reports.byCity}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
                        <XAxis dataKey="name" stroke="#64748B" style={{ fontSize: '12px' }} />
                        <YAxis stroke="#64748B" style={{ fontSize: '12px' }} />
                        <Tooltip 
                          contentStyle={{ 
                            backgroundColor: '#fff', 
                            border: '1px solid #E2E8F0',
                            borderRadius: '8px',
                            boxShadow: '0 4px 6px rgba(0,0,0,0.1)'
                          }}
                        />
                        <Bar dataKey="total" fill="#0EA5E9" radius={[8, 8, 0, 0]} />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                )}

                {/* Gráfico de Presenças por Unidade */}
                {reports.byUnit.length > 0 && (
                  <div className="bg-white border border-slate-100 rounded-xl p-6 shadow-sm">
                    <h2 className="text-xl font-heading font-semibold text-slate-900 mb-6">Top 10 Unidades (Presenças)</h2>
                    <ResponsiveContainer width="100%" height={400}>
                      <BarChart data={reports.byUnit} layout="vertical">
                        <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
                        <XAxis type="number" stroke="#64748B" style={{ fontSize: '12px' }} />
                        <YAxis 
                          type="category" 
                          dataKey="name" 
                          width={200}
                          stroke="#64748B" 
                          style={{ fontSize: '11px' }}
                        />
                        <Tooltip 
                          contentStyle={{ 
                            backgroundColor: '#fff', 
                            border: '1px solid #E2E8F0',
                            borderRadius: '8px',
                            boxShadow: '0 4px 6px rgba(0,0,0,0.1)'
                          }}
                        />
                        <Bar dataKey="total" fill="#334155" radius={[0, 8, 8, 0]} />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                )}

                {/* Gráfico de Pizza - Status dos Atendentes */}
                {reports.statusData && (
                  <div className="bg-white border border-slate-100 rounded-xl p-6 shadow-sm">
                    <h2 className="text-xl font-heading font-semibold text-slate-900 mb-6">Status dos Atendentes</h2>
                    <ResponsiveContainer width="100%" height={300}>
                      <PieChart>
                        <Pie
                          data={reports.statusData}
                          cx="50%"
                          cy="50%"
                          labelLine={false}
                          label={({ name, value }) => `${name}: ${value}`}
                          outerRadius={100}
                          fill="#8884d8"
                          dataKey="value"
                        >
                          {reports.statusData.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={entry.color} />
                          ))}
                        </Pie>
                        <Tooltip />
                      </PieChart>
                    </ResponsiveContainer>
                  </div>
                )}
              </div>
            )}
          </div>
        </main>
      </div>
    </div>
  );
};
export default ReportsPage;
