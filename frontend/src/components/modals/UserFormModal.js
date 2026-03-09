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

const roles = [
  { value: 'atendente', label: 'Atendente' },
  { value: 'secretario_local', label: 'Secretário Local' },
  { value: 'secretario_regional', label: 'Secretário Regional' },
  { value: 'anciao_coordenador', label: 'Ancião Coordenador' },
  { value: 'consulta', label: 'Consulta' }
];

export const UserFormModal = ({ open, onClose, onSuccess }) => {
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    email: '',
    nome_completo: '',
    senha: '',
    cidade: '',
    role: 'atendente'
  });

  useEffect(() => {
    if (!open) {
      setFormData({
        email: '',
        nome_completo: '',
        senha: '',
        cidade: '',
        role: 'atendente'
      });
    }
  }, [open]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.email || !formData.nome_completo || !formData.senha || !formData.cidade) {
      toast.error('Preencha todos os campos obrigatórios');
      return;
    }

    setLoading(true);
    try {
      await authApi.register(formData);
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
              onChange={(e) => setFormData({ ...formData, nome_completo: e.target.value })}
              placeholder="Nome completo do colaborador"
              required
            />
          </div>

          <div>
            <label className="text-sm font-medium text-slate-700 mb-2 block">Email *</label>
            <Input
              data-testid="user-email-input"
              type="email"
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              placeholder="email@exemplo.com"
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
            <label className="text-sm font-medium text-slate-700 mb-2 block">Função *</label>
            <Select value={formData.role} onValueChange={(value) => setFormData({ ...formData, role: value })}>
              <SelectTrigger data-testid="user-role-select">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {roles.map((role) => (
                  <SelectItem key={role.value} value={role.value}>{role.label}</SelectItem>
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
