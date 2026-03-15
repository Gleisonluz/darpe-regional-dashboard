import React, { useState, useEffect } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { toast } from 'sonner';
import { authApi } from '@/utils/api';

const cidades = [
  'Itajaí', 'Balneário Camboriú', 'Camboriú', 'Penha', 'Navegantes',
  'Barra Velha', 'Balneário Piçarras', 'São João do Itaperiú',
  'Ilhota', 'Guabiruba', 'Botuverá', 'Nova Trento', 'Brusque', 'Blumenau'
];

const funcoesDarpe = [
  { value: 'Atendente', label: 'Atendente' },
  { value: 'Secretário Local', label: 'Secretário Local' },
  { value: 'Secretário Regional', label: 'Secretário Regional' },
  { value: 'Ancião Coordenador', label: 'Ancião Coordenador' }
];


const formatWhatsapp = (value) => {
  const digits = value.replace(/\D/g, '').slice(0, 11);

  if (digits.length <= 2) return digits;
  if (digits.length <= 6) return `(${digits.slice(0, 2)}) ${digits.slice(2)}`;
  if (digits.length <= 10) {
    return `(${digits.slice(0, 2)}) ${digits.slice(2, 6)}-${digits.slice(6)}`;
  }
  return `(${digits.slice(0, 2)}) ${digits.slice(2, 7)}-${digits.slice(7)}`;
};

const normalizeWhatsapp = (value) => {
  const digits = value.replace(/\D/g, '');
  return `+55${digits}`;
};

export const UserFormModal = ({ open, onClose, onSuccess }) => {
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    whatsapp: '',
    nome_completo: '',
    senha: '',
    cidade: '',
    localidade: '',
    funcoes_darpe: ['Atendente']
  });

  useEffect(() => {
    if (!open) {
      setFormData({
        whatsapp: '',
        nome_completo: '',
        senha: '',
        cidade: '',
        localidade: '',
        funcoes_darpe: ['Atendente']
      });
    }
  }, [open]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.whatsapp || !formData.nome_completo || !formData.senha || !formData.cidade) {
      toast.error('Preencha todos os campos obrigatórios');
      return;
    }

    setLoading(true);
    try {
      const payload = {
        ...formData,
        whatsapp: normalizeWhatsapp(formData.whatsapp)
      };
      
      await authApi.register(payload);
      toast.success('Colaborador cadastrado com sucesso! Status: Pendente de aprovação');
      onSuccess();
      onClose();
    } catch (error) {
      console.error('Erro ao cadastrar colaborador:', error);
      toast.error(error.response?.data?.detail || 'Erro ao cadastrar colaborador');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle>Novo Colaborador</DialogTitle>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="text-sm font-medium text-slate-700 mb-2 block">Nome Completo *</label>
            <Input
  data-testid="user-name-input"
  value={formData.nome_completo}
  onChange={(e) =>
    setFormData({ ...formData, nome_completo: e.target.value })
  }
  placeholder="Nome completo do colaborador"
  required
/>
          </div>

          <div>
            <label className="text-sm font-medium text-slate-700 mb-2 block">WhatsApp *</label>
            <Input
              data-testid="user-whatsapp-input"
              type="tel"
              value={formData.whatsapp}
              onChange={(e) =>
                setFormData({ ...formData, whatsapp: formatWhatsapp(e.target.value) })
              }
              placeholder="(__) _____-____"
              required
            />
          </div>

          <div>
            <label className="text-sm font-medium text-slate-700 mb-2 block">Senha *</label>
            <Input
              data-testid="user-password-input"
              type="password"
              value={formData.senha}
              onChange={(e) => setFormData({ ...formData, senha: e.target.value })}
              placeholder="Senha de acesso"
              required
            />
          </div>

          <div>
            <label className="text-sm font-medium text-slate-700 mb-2 block">Cidade *</label>
            <Select value={formData.cidade} onValueChange={(value) => setFormData({ ...formData, cidade: value })}>
              <SelectTrigger data-testid="user-city-select">
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
            <label className="text-sm font-medium text-slate-700 mb-2 block">Localidade</label>
            <Input
              data-testid="user-locality-input"
              value={formData.localidade}
              onChange={(e) => setFormData({ ...formData, localidade: e.target.value })}
              placeholder="Ex: Congregação Central"
            />
          </div>

          <div>
            <label className="text-sm font-medium text-slate-700 mb-2 block">Função DARPE *</label>
            <Select 
              value={formData.funcoes_darpe[0]} 
              onValueChange={(value) =>
                setFormData({
                  ...formData,
                  funcoes_darpe:
                    value === 'Ancião Coordenador'
                      ? ['Ancião Coordenador']
                      : [value]
                })
              }
            >
              <SelectTrigger data-testid="user-function-select">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {funcoesDarpe.map((funcao) => (
                  <SelectItem key={funcao.value} value={funcao.value}>{funcao.label}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={onClose} disabled={loading}>
              Cancelar
            </Button>
            <Button type="submit" data-testid="save-user-button" disabled={loading} className="bg-accent hover:bg-accent/90 text-white">
              {loading ? 'Cadastrando...' : 'Cadastrar'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
};
