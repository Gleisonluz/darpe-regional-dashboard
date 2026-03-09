import React, { useState, useEffect } from 'react';
import { Sidebar } from '@/components/Sidebar';
import { TopBar } from '@/components/TopBar';
import { unitsApi, attendanceApi } from '@/utils/api';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import { toast } from 'sonner';
import { ClipboardCheck, History } from 'lucide-react';

const AttendancePage = () => {
  const [units, setUnits] = useState([]);
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [formData, setFormData] = useState({
    unidade_id: '',
    funcao: 'pregacao',
    observacao: ''
  });

  const funcoes = [
    { value: 'pregacao', label: 'Pregação' },
    { value: 'musica', label: 'Música' },
    { value: 'organizacao', label: 'Organização' },
    { value: 'apoio', label: 'Apoio' }
  ];

  useEffect(() => {
    loadUnits();
    loadRecords();
  }, []);

  const loadUnits = async () => {
    try {
      const response = await unitsApi.getAll();
      setUnits(response.data);
    } catch (error) {
      console.error('Erro ao carregar unidades:', error);
    }
  };

  const loadRecords = async () => {
    try {
      const response = await attendanceApi.getMyRecords();
      setRecords(response.data);
    } catch (error) {
      console.error('Erro ao carregar registros:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.unidade_id) {
      toast.error('Selecione uma unidade');
      return;
    }

    setLoading(true);
    try {
      await attendanceApi.register(formData);
      toast.success('Presença registrada com sucesso!');
      setFormData({ unidade_id: '', funcao: 'pregacao', observacao: '' });
      loadRecords();
    } catch (error) {
      console.error('Erro ao registrar presença:', error);
      toast.error(error.response?.data?.detail || 'Erro ao registrar presença');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleString('pt-BR');
  };

  return (
    <div className="flex min-h-screen bg-muted">
      <Sidebar />
      
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
          <div className="max-w-4xl mx-auto">
            <div className="mb-8">
              <h1 className="text-3xl md:text-4xl font-heading font-bold text-slate-900 mb-2">
                Registrar Presença
              </h1>
              <p className="text-slate-600">
                Registre sua presença em cada atendimento para manter sua credencial ativa
              </p>
            </div>

            {/* Formulário de Registro */}
            <div className="bg-white rounded-xl border border-slate-100 p-6 shadow-sm mb-8">
              <div className="flex items-center gap-3 mb-6">
                <div className="w-10 h-10 bg-accent/10 rounded-lg flex items-center justify-center">
                  <ClipboardCheck className="w-5 h-5 text-accent" />
                </div>
                <h2 className="text-xl font-heading font-semibold text-slate-900">Nova Presença</h2>
              </div>

              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label className="text-sm font-medium text-slate-700 mb-2 block">Unidade</label>
                  <Select
                    value={formData.unidade_id}
                    onValueChange={(value) => setFormData({ ...formData, unidade_id: value })}
                  >
                    <SelectTrigger data-testid="attendance-unit-select">
                      <SelectValue placeholder="Selecione a unidade" />
                    </SelectTrigger>
                    <SelectContent>
                      {units.map((unit) => (
                        <SelectItem key={unit.id} value={unit.id}>
                          {unit.nome} - {unit.cidade}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <label className="text-sm font-medium text-slate-700 mb-2 block">Função no Atendimento</label>
                  <Select
                    value={formData.funcao}
                    onValueChange={(value) => setFormData({ ...formData, funcao: value })}
                  >
                    <SelectTrigger data-testid="attendance-function-select">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {funcoes.map((funcao) => (
                        <SelectItem key={funcao.value} value={funcao.value}>
                          {funcao.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <label className="text-sm font-medium text-slate-700 mb-2 block">Observação (Opcional)</label>
                  <Textarea
                    data-testid="attendance-observation-input"
                    placeholder="Adicione alguma observação se necessário..."
                    value={formData.observacao}
                    onChange={(e) => setFormData({ ...formData, observacao: e.target.value })}
                    rows={3}
                  />
                </div>

                <Button
                  data-testid="submit-attendance-button"
                  type="submit"
                  className="w-full bg-accent hover:bg-accent/90 text-white rounded-full"
                  disabled={loading}
                >
                  {loading ? 'Registrando...' : 'Registrar Presença'}
                </Button>
              </form>
            </div>

            {/* Histórico */}
            <div className="bg-white rounded-xl border border-slate-100 p-6 shadow-sm">
              <div className="flex items-center gap-3 mb-6">
                <div className="w-10 h-10 bg-accent/10 rounded-lg flex items-center justify-center">
                  <History className="w-5 h-5 text-accent" />
                </div>
                <h2 className="text-xl font-heading font-semibold text-slate-900">Histórico de Presenças</h2>
              </div>

              {records.length === 0 ? (
                <p className="text-center text-slate-600 py-8">Nenhuma presença registrada ainda</p>
              ) : (
                <div className="space-y-3">
                  {records.map((record) => {
                    const unit = units.find(u => u.id === record.unidade_id);
                    return (
                      <div
                        key={record.id}
                        data-testid={`attendance-record-${record.id}`}
                        className="p-4 bg-slate-50 rounded-lg hover:bg-slate-100 transition-colors"
                      >
                        <div className="flex justify-between items-start mb-2">
                          <div>
                            <p className="font-medium text-slate-900">
                              {unit ? `${unit.nome} - ${unit.cidade}` : 'Unidade não encontrada'}
                            </p>
                            <p className="text-sm text-slate-600 capitalize">
                              Função: {record.funcao.replace('_', ' ')}
                            </p>
                          </div>
                          <span className="text-sm text-slate-500">{formatDate(record.data)}</span>
                        </div>
                        {record.observacao && (
                          <p className="text-sm text-slate-600 mt-2 italic">{record.observacao}</p>
                        )}
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          </div>
        </main>
      </div>
    </div>
  );
};

export default AttendancePage;
