import React, { useState, useEffect } from 'react';
import { Sidebar } from '@/components/Sidebar';
import { TopBar } from '@/components/TopBar';
import { reportsApi } from '@/utils/api';
import { Calendar, MapPin, Clock } from 'lucide-react';

const AgendaPage = () => {
  const [agenda, setAgenda] = useState([]);
  const [loading, setLoading] = useState(true);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  useEffect(() => {
    loadAgenda();
  }, []);

  const loadAgenda = async () => {
    try {
      const response = await reportsApi.agenda();
      setAgenda(response.data.data);
    } catch (error) {
      console.error('Erro ao carregar agenda:', error);
    } finally {
      setLoading(false);
    }
  };

  const diasOrdenados = ['segunda', 'terca', 'quarta', 'quinta', 'sexta', 'sabado', 'domingo'];
  const groupByDay = () => {
    const grouped = {};
    agenda.forEach(item => {
      if (!grouped[item.dia_semana]) grouped[item.dia_semana] = [];
      grouped[item.dia_semana].push(item);
    });
    return grouped;
  };

  const grouped = groupByDay();

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
          <div className="max-w-6xl mx-auto">
            <div className="mb-8">
              <h1 className="text-3xl font-heading font-bold text-slate-900 mb-2">Agenda Semanal</h1>
              <p className="text-slate-600">Próximos atendimentos da regional</p>
            </div>

            {loading ? (
              <div className="text-center py-12">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
              </div>
            ) : (
              <div className="space-y-6">
                {diasOrdenados.map(dia => {
                  const items = grouped[dia] || [];
                  if (items.length === 0) return null;
                  const diaNome = { segunda: 'Segunda-feira', terca: 'Terça-feira', quarta: 'Quarta-feira', quinta: 'Quinta-feira', sexta: 'Sexta-feira', sabado: 'Sábado', domingo: 'Domingo' }[dia];
                  return (
                    <div key={dia} className="bg-white rounded-xl border border-slate-100 p-6 shadow-sm">
                      <h2 className="text-xl font-heading font-semibold text-slate-900 mb-4">{diaNome}</h2>
                      <div className="space-y-3">
                        {items.map(item => (
                          <div key={item.id} data-testid={`agenda-${item.id}`} className="p-4 bg-slate-50 rounded-lg flex justify-between items-start">
                            <div>
                              <p className="font-medium text-slate-900">{item.nome}</p>
                              <div className="flex items-center gap-4 mt-2 text-sm text-slate-600">
                                <span className="flex items-center gap-1"><MapPin className="w-4 h-4" />{item.cidade}</span>
                                <span className="flex items-center gap-1"><Clock className="w-4 h-4" />{item.horario}</span>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </main>
      </div>
    </div>
  );
};
export default AgendaPage;
