import React, { useState, useEffect } from 'react';
import { Sidebar } from '@/components/Sidebar';
import { TopBar } from '@/components/TopBar';
import { unitsApi, serviceApi, usersApi } from '@/utils/api';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import { toast } from 'sonner';
import { FileText, History } from 'lucide-react';

const ServicePage = () => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [units, setUnits] = useState([]);
  const [users, setUsers] = useState([]);
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    unidade_id: '',
    data: new Date().toISOString().split('T')[0],
    hora_inicio: '',
    hora_termino: '',
    pregador_id: '',
    livro_biblico: '',
    capitulo: '',
    verso_inicial: '',
    verso_final: '',
    hinos_cantados: '',
    qtd_musicos: '',
    qtd_colaboradores: '',
    qtd_atendentes: '',
    observacoes: ''
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [unitsRes, usersRes, recordsRes] = await Promise.all([
        unitsApi.getAll(),
        usersApi.getAll(),
        serviceApi.getAll()
      ]);
      setUnits(unitsRes.data);
      setUsers(usersRes.data.filter(u => u.status === 'ativo'));
      setRecords(recordsRes.data);
    } catch (error) {
      console.error('Erro ao carregar dados:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.unidade_id || !formData.data || !formData.hora_inicio || !formData.hora_termino || !formData.pregador_id) {
      toast.error('Preencha todos os campos obrigatórios');
      return;
    }

    setLoading(true);
    try {
      const payload = {
        ...formData,
        data: new Date(formData.data).toISOString(),
        capitulo: parseInt(formData.capitulo) || 0,
        verso_inicial: parseInt(formData.verso_inicial) || 0,
        verso_final: parseInt(formData.verso_final) || 0,
        hinos_cantados: formData.hinos_cantados.split(',').map(h => parseInt(h.trim())).filter(h => !isNaN(h)),
        qtd_musicos: parseInt(formData.qtd_musicos) || 0,
        qtd_colaboradores: parseInt(formData.qtd_colaboradores) || 0,
        qtd_atendentes: parseInt(formData.qtd_atendentes) || 0
      };

      await serviceApi.register(payload);
      toast.success('Atendimento registrado com sucesso!');
      
      setFormData({
        unidade_id: '',
        data: new Date().toISOString().split('T')[0],
        hora_inicio: '',
        hora_termino: '',
        pregador_id: '',
        livro_biblico: '',
        capitulo: '',
        verso_inicial: '',
        verso_final: '',
        hinos_cantados: '',
        qtd_musicos: '',
        qtd_colaboradores: '',
        qtd_atendentes: '',
        observacoes: ''
      });
      
      loadData();
    } catch (error) {
      console.error('Erro ao registrar atendimento:', error);
      toast.error(error.response?.data?.detail || 'Erro ao registrar atendimento');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('pt-BR');
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
          <div className="max-w-5xl mx-auto">
            <div className="mb-8">
              <h1 className="text-3xl font-heading font-bold text-slate-900 mb-2">Registrar Atendimento Completo</h1>
              <p className="text-slate-600">Registre todos os detalhes do atendimento realizado</p>
            </div>

            {/* Formulário */}
            <div className="bg-white rounded-xl border border-slate-100 p-6 shadow-sm mb-8">
              <div className="flex items-center gap-3 mb-6">
                <div className="w-10 h-10 bg-accent/10 rounded-lg flex items-center justify-center">
                  <FileText className="w-5 h-5 text-accent" />
                </div>
                <h2 className="text-xl font-heading font-semibold text-slate-900">Novo Registro</h2>
              </div>

              <form onSubmit={handleSubmit} className="space-y-6">
                {/* Informações Básicas */}
                <div>
                  <h3 className="text-sm font-semibold text-slate-700 mb-3 uppercase tracking-wider">Informações Básicas</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="text-sm font-medium text-slate-700 mb-2 block">Unidade *</label>
                      <Select value={formData.unidade_id} onValueChange={(value) => setFormData({ ...formData, unidade_id: value })}>
                        <SelectTrigger data-testid="service-unit-select">
                          <SelectValue placeholder="Selecione a unidade" />
                        </SelectTrigger>
                        <SelectContent>
                          {units.map((unit) => (
                            <SelectItem key={unit.id} value={unit.id}>{unit.nome} - {unit.cidade}</SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>

                    <div>
                      <label className="text-sm font-medium text-slate-700 mb-2 block">Data *</label>
                      <Input
                        type="date"
                        value={formData.data}
                        onChange={(e) => setFormData({ ...formData, data: e.target.value })}
                        required
                      />
                    </div>

                    <div>
                      <label className="text-sm font-medium text-slate-700 mb-2 block">Hora Início *</label>
                      <Input
                        type="time"
                        value={formData.hora_inicio}
                        onChange={(e) => setFormData({ ...formData, hora_inicio: e.target.value })}
                        required
                      />
                    </div>

                    <div>
                      <label className="text-sm font-medium text-slate-700 mb-2 block">Hora Término *</label>
                      <Input
                        type="time"
                        value={formData.hora_termino}
                        onChange={(e) => setFormData({ ...formData, hora_termino: e.target.value })}
                        required
                      />
                    </div>
                  </div>
                </div>

                {/* Pregação */}
                <div>
                  <h3 className="text-sm font-semibold text-slate-700 mb-3 uppercase tracking-wider">Pregação</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="md:col-span-2">
                      <label className="text-sm font-medium text-slate-700 mb-2 block">Pregador *</label>
                      <Select value={formData.pregador_id} onValueChange={(value) => setFormData({ ...formData, pregador_id: value })}>
                        <SelectTrigger>
                          <SelectValue placeholder="Selecione o pregador" />
                        </SelectTrigger>
                        <SelectContent>
                          {users.map((user) => (
                            <SelectItem key={user.id} value={user.id}>{user.nome_completo}</SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>

                    <div>
                      <label className="text-sm font-medium text-slate-700 mb-2 block">Livro Bíblico</label>
                      <Input
                        value={formData.livro_biblico}
                        onChange={(e) => setFormData({ ...formData, livro_biblico: e.target.value })}
                        placeholder="Ex: João"
                      />
                    </div>

                    <div>
                      <label className="text-sm font-medium text-slate-700 mb-2 block">Capítulo</label>
                      <Input
                        type="number"
                        value={formData.capitulo}
                        onChange={(e) => setFormData({ ...formData, capitulo: e.target.value })}
                        placeholder="Ex: 3"
                      />
                    </div>

                    <div>
                      <label className="text-sm font-medium text-slate-700 mb-2 block">Verso Inicial</label>
                      <Input
                        type="number"
                        value={formData.verso_inicial}
                        onChange={(e) => setFormData({ ...formData, verso_inicial: e.target.value })}
                        placeholder="Ex: 16"
                      />
                    </div>

                    <div>
                      <label className="text-sm font-medium text-slate-700 mb-2 block">Verso Final</label>
                      <Input
                        type="number"
                        value={formData.verso_final}
                        onChange={(e) => setFormData({ ...formData, verso_final: e.target.value })}
                        placeholder="Ex: 21"
                      />
                    </div>
                  </div>
                </div>

                {/* Quantidades */}
                <div>
                  <h3 className="text-sm font-semibold text-slate-700 mb-3 uppercase tracking-wider">Presença e Participação</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="text-sm font-medium text-slate-700 mb-2 block">Hinos Cantados</label>
                      <Input
                        value={formData.hinos_cantados}
                        onChange={(e) => setFormData({ ...formData, hinos_cantados: e.target.value })}
                        placeholder="Ex: 120, 145, 200"
                      />
                      <p className="text-xs text-slate-500 mt-1">Separe os números por vírgula</p>
                    </div>

                    <div>
                      <label className="text-sm font-medium text-slate-700 mb-2 block">Quantidade de Músicos</label>
                      <Input
                        type="number"
                        value={formData.qtd_musicos}
                        onChange={(e) => setFormData({ ...formData, qtd_musicos: e.target.value })}
                        placeholder="0"
                      />
                    </div>

                    <div>
                      <label className="text-sm font-medium text-slate-700 mb-2 block">Quantidade de Colaboradores</label>
                      <Input
                        type="number"
                        value={formData.qtd_colaboradores}
                        onChange={(e) => setFormData({ ...formData, qtd_colaboradores: e.target.value })}
                        placeholder="0"
                      />
                    </div>

                    <div>
                      <label className="text-sm font-medium text-slate-700 mb-2 block">Quantidade de Atendentes</label>
                      <Input
                        type="number"
                        value={formData.qtd_atendentes}
                        onChange={(e) => setFormData({ ...formData, qtd_atendentes: e.target.value })}
                        placeholder="0"
                      />
                    </div>
                  </div>
                </div>

                {/* Observações */}
                <div>
                  <label className="text-sm font-medium text-slate-700 mb-2 block">Observações</label>
                  <Textarea
                    value={formData.observacoes}
                    onChange={(e) => setFormData({ ...formData, observacoes: e.target.value })}
                    placeholder="Informações adicionais sobre o atendimento..."
                    rows={3}
                  />
                </div>

                <Button
                  type="submit"
                  data-testid="submit-service-button"
                  className="w-full bg-accent hover:bg-accent/90 text-white rounded-full"
                  disabled={loading}
                >
                  {loading ? 'Registrando...' : 'Registrar Atendimento'}
                </Button>
              </form>
            </div>

            {/* Histórico */}
            <div className="bg-white rounded-xl border border-slate-100 p-6 shadow-sm">
              <div className="flex items-center gap-3 mb-6">
                <div className="w-10 h-10 bg-accent/10 rounded-lg flex items-center justify-center">
                  <History className="w-5 h-5 text-accent" />
                </div>
                <h2 className="text-xl font-heading font-semibold text-slate-900">Atendimentos Recentes</h2>
              </div>

              {records.length === 0 ? (
                <p className="text-center text-slate-600 py-8">Nenhum atendimento registrado ainda</p>
              ) : (
                <div className="space-y-3">
                  {records.slice(0, 5).map((record) => {
                    const unit = units.find(u => u.id === record.unidade_id);
                    const pregador = users.find(u => u.id === record.pregador_id);
                    return (
                      <div key={record.id} className="p-4 bg-slate-50 rounded-lg hover:bg-slate-100 transition-colors">
                        <div className="flex justify-between items-start mb-2">
                          <div>
                            <p className="font-medium text-slate-900">
                              {unit ? `${unit.nome} - ${unit.cidade}` : 'Unidade não encontrada'}
                            </p>
                            <p className="text-sm text-slate-600">
                              Pregador: {pregador ? pregador.nome_completo : 'Não informado'}
                            </p>
                          </div>
                          <span className="text-sm text-slate-500">{formatDate(record.data)}</span>
                        </div>
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-xs text-slate-600 mt-3">
                          <span>⏰ {record.hora_inicio} - {record.hora_termino}</span>
                          {record.livro_biblico && (
                            <span>📖 {record.livro_biblico} {record.capitulo}:{record.verso_inicial}-{record.verso_final}</span>
                          )}
                          <span>🎵 {record.qtd_musicos} músicos</span>
                          <span>👥 {record.qtd_atendentes} atendentes</span>
                        </div>
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
export default ServicePage;
