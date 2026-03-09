import React, { useState, useEffect } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import { toast } from 'sonner';
import { unitsApi } from '@/utils/api';

const cidades = [
  'Itajaí', 'Balneário Camboriú', 'Camboriú', 'Penha', 'Navegantes',
  'Barra Velha', 'Balneário Piçarras', 'São João do Itaperiú',
  'Ilhota', 'Guabiruba', 'Botuverá', 'Nova Trento', 'Brusque', 'Blumenau'
];

const diasSemana = [
  { value: 'segunda', label: 'Segunda-feira' },
  { value: 'terca', label: 'Terça-feira' },
  { value: 'quarta', label: 'Quarta-feira' },
  { value: 'quinta', label: 'Quinta-feira' },
  { value: 'sexta', label: 'Sexta-feira' },
  { value: 'sabado', label: 'Sábado' },
  { value: 'domingo', label: 'Domingo' }
];

const setores = [
  { value: 'SETOR 1 - Sistemas de Ressocialização e Socioeducativos', label: 'SETOR 1 - Sistemas de Ressocialização e Socioeducativos' },
  { value: 'SETOR 2 - Clínica de Dependentes e Albergues', label: 'SETOR 2 - Clínica de Dependentes e Albergues' },
  { value: 'SETOR 3 - Forças de Segurança', label: 'SETOR 3 - Forças de Segurança' },
  { value: 'SETOR 4 - Hospitais, Instituição para Idosos, Setor Educacional', label: 'SETOR 4 - Hospitais, Instituição para Idosos, Setor Educacional' }
];

const tiposServico = [
  { value: 'Reunião de Evangelização', label: 'Reunião de Evangelização' },
  { value: 'Projeto Música, Acolhimento e Espiritualidade (PMAE)', label: 'Projeto Música, Acolhimento e Espiritualidade (PMAE)' }
];

export const UnitFormModal = ({ open, onClose, unit, onSuccess }) => {
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    nome: '',
    cidade: '',
    setor: '',
    tipo_servico: '',
    dia_semana: 'domingo',
    horario: '',
    telefone_contato: '',
    endereco: '',
    observacoes: ''
  });

  useEffect(() => {
    if (unit) {
      setFormData({
        nome: unit.nome || '',
        cidade: unit.cidade || '',
        setor: unit.setor || '',
        tipo_servico: unit.tipo_servico || '',
        dia_semana: unit.dia_semana || 'domingo',
        horario: unit.horario || '',
        telefone_contato: unit.telefone_contato || '',
        endereco: unit.endereco || '',
        observacoes: unit.observacoes || ''
      });
    } else {
      setFormData({
        nome: '',
        cidade: '',
        setor: '',
        tipo_servico: '',
        dia_semana: 'domingo',
        horario: '',
        telefone_contato: '',
        endereco: '',
        observacoes: ''
      });
    }
  }, [unit, open]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.nome || !formData.cidade || !formData.setor || !formData.tipo_servico || !formData.horario) {
      toast.error('Preencha todos os campos obrigatórios');
      return;
    }

    setLoading(true);
    try {
      if (unit) {
        await unitsApi.update(unit.id, formData);
        toast.success('Unidade atualizada com sucesso!');
      } else {
        await unitsApi.create(formData);
        toast.success('Unidade criada com sucesso!');
      }
      onSuccess();
      onClose();
    } catch (error) {
      console.error('Erro ao salvar unidade:', error);
      toast.error(error.response?.data?.detail || 'Erro ao salvar unidade');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>{unit ? 'Editar Unidade' : 'Nova Unidade'}</DialogTitle>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="text-sm font-medium text-slate-700 mb-2 block">Nome da Unidade *</label>
            <Input
              data-testid="unit-name-input"
              value={formData.nome}
              onChange={(e) => setFormData({ ...formData, nome: e.target.value })}
              placeholder="Ex: Centro de Evangelização Itajaí Centro"
              required
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="text-sm font-medium text-slate-700 mb-2 block">Cidade *</label>
              <Select value={formData.cidade} onValueChange={(value) => setFormData({ ...formData, cidade: value })}>
                <SelectTrigger data-testid="unit-city-select">
                  <SelectValue placeholder="Selecione a cidade" />
                </SelectTrigger>
                <SelectContent>
                  {cidades.map((cidade) => (
                    <SelectItem key={cidade} value={cidade}>{cidade}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div>
              <label className="text-sm font-medium text-slate-700 mb-2 block">Setor *</label>
              <Select value={formData.setor} onValueChange={(value) => setFormData({ ...formData, setor: value })}>
                <SelectTrigger data-testid="unit-sector-select">
                  <SelectValue placeholder="Selecione o setor" />
                </SelectTrigger>
                <SelectContent>
                  {setores.map((setor) => (
                    <SelectItem key={setor.value} value={setor.value}>{setor.label}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="text-sm font-medium text-slate-700 mb-2 block">Tipo de Serviço *</label>
              <Select value={formData.tipo_servico} onValueChange={(value) => setFormData({ ...formData, tipo_servico: value })}>
                <SelectTrigger data-testid="unit-service-select">
                  <SelectValue placeholder="Selecione o tipo" />
                </SelectTrigger>
                <SelectContent>
                  {tiposServico.map((tipo) => (
                    <SelectItem key={tipo.value} value={tipo.value}>{tipo.label}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div>
              <label className="text-sm font-medium text-slate-700 mb-2 block">Dia da Semana *</label>
              <Select value={formData.dia_semana} onValueChange={(value) => setFormData({ ...formData, dia_semana: value })}>
                <SelectTrigger data-testid="unit-day-select">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {diasSemana.map((dia) => (
                    <SelectItem key={dia.value} value={dia.value}>{dia.label}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="text-sm font-medium text-slate-700 mb-2 block">Horário *</label>
              <Input
                data-testid="unit-time-input"
                value={formData.horario}
                onChange={(e) => setFormData({ ...formData, horario: e.target.value })}
                placeholder="Ex: 19:30"
                required
              />
            </div>

            <div>
              <label className="text-sm font-medium text-slate-700 mb-2 block">Telefone de Contato</label>
              <Input
                data-testid="unit-phone-input"
                value={formData.telefone_contato}
                onChange={(e) => setFormData({ ...formData, telefone_contato: e.target.value })}
                placeholder="Ex: (47) 99999-9999"
              />
            </div>
          </div>

          <div>
            <label className="text-sm font-medium text-slate-700 mb-2 block">Endereço</label>
            <Input
              data-testid="unit-address-input"
              value={formData.endereco}
              onChange={(e) => setFormData({ ...formData, endereco: e.target.value })}
              placeholder="Ex: Rua das Flores, 123 - Centro"
            />
          </div>

          <div>
            <label className="text-sm font-medium text-slate-700 mb-2 block">Observações</label>
            <Textarea
              data-testid="unit-notes-input"
              value={formData.observacoes}
              onChange={(e) => setFormData({ ...formData, observacoes: e.target.value })}
              placeholder="Informações adicionais..."
              rows={3}
            />
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={onClose} disabled={loading}>
              Cancelar
            </Button>
            <Button type="submit" data-testid="save-unit-button" disabled={loading} className="bg-accent hover:bg-accent/90 text-white">
              {loading ? 'Salvando...' : unit ? 'Atualizar' : 'Criar Unidade'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
};
