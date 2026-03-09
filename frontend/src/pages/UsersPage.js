import React, { useState, useEffect } from 'react';
import { Sidebar } from '@/components/Sidebar';
import { TopBar } from '@/components/TopBar';
import { usersApi } from '@/utils/api';
import { Button } from '@/components/ui/button';
import { UserCheck, UserX, Users as UsersIcon } from 'lucide-react';
import { toast } from 'sonner';

const UsersPage = () => {
  const [users, setUsers] = useState([]);
  const [filter, setFilter] = useState('all');
  const [loading, setLoading] = useState(true);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  useEffect(() => {
    loadUsers();
  }, [filter]);

  const loadUsers = async () => {
    try {
      const params = {};
      if (filter === 'pending') params.status = 'pendente';
      else if (filter === 'blocked') params.status = 'bloqueado_por_inatividade';
      const response = await usersApi.getAll(params);
      setUsers(response.data);
    } catch (error) {
      console.error('Erro ao carregar usuários:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async (userId) => {
    try {
      await usersApi.approve(userId);
      toast.success('Usuário aprovado com sucesso!');
      loadUsers();
    } catch (error) {
      toast.error('Erro ao aprovar usuário');
    }
  };

  const handleReactivate = async (userId) => {
    try {
      await usersApi.reactivate(userId);
      toast.success('Usuário reativado com sucesso!');
      loadUsers();
    } catch (error) {
      toast.error('Erro ao reativar usuário');
    }
  };

  const getStatusBadge = (status) => {
    const configs = {
      ativo: { label: 'Ativo', class: 'bg-emerald-50 text-emerald-700 border-emerald-200' },
      pendente: { label: 'Pendente', class: 'bg-amber-50 text-amber-700 border-amber-200' },
      bloqueado_por_inatividade: { label: 'Bloqueado', class: 'bg-red-50 text-red-700 border-red-200' }
    };
    const config = configs[status] || configs.ativo;
    return <span className={`text-xs px-2 py-1 rounded-full border ${config.class}`}>{config.label}</span>;
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
          <div className="max-w-6xl mx-auto">
            <div className="mb-8">
              <h1 className="text-3xl font-heading font-bold text-slate-900 mb-2">Colaboradores</h1>
              <p className="text-slate-600">Gerencie colaboradores e aprovações</p>
            </div>

            <div className="flex gap-2 mb-6">
              <Button data-testid="filter-all" onClick={() => setFilter('all')} variant={filter === 'all' ? 'default' : 'outline'} className="rounded-full">Todos</Button>
              <Button data-testid="filter-pending" onClick={() => setFilter('pending')} variant={filter === 'pending' ? 'default' : 'outline'} className="rounded-full">Pendentes</Button>
              <Button data-testid="filter-blocked" onClick={() => setFilter('blocked')} variant={filter === 'blocked' ? 'default' : 'outline'} className="rounded-full">Bloqueados</Button>
            </div>

            {loading ? (
              <div className="text-center py-12">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
              </div>
            ) : (
              <div className="bg-white rounded-xl border border-slate-100 shadow-sm overflow-hidden">
                {users.length === 0 ? (
                  <p className="text-center py-12 text-slate-600">Nenhum usuário encontrado</p>
                ) : (
                  <div className="divide-y divide-slate-100">
                    {users.map((user) => (
                      <div key={user.id} data-testid={`user-${user.id}`} className="p-4 hover:bg-slate-50 transition-colors">
                        <div className="flex items-center justify-between gap-4">
                          <div className="flex items-center gap-3 flex-1">
                            <div className="w-12 h-12 bg-accent/10 rounded-full flex items-center justify-center text-accent font-semibold">
                              {user.nome_completo.charAt(0)}
                            </div>
                            <div className="flex-1 min-w-0">
                              <p className="font-medium text-slate-900 truncate">{user.nome_completo}</p>
                              <p className="text-sm text-slate-600 truncate">{user.email}</p>
                              <div className="flex items-center gap-2 mt-1">
                                <span className="text-xs text-slate-500 capitalize">{user.role.replace('_', ' ')}</span>
                                {user.cidade && <span className="text-xs text-slate-500">• {user.cidade}</span>}
                              </div>
                            </div>
                          </div>
                          <div className="flex items-center gap-2">
                            {getStatusBadge(user.status)}
                            {user.status === 'pendente' && (
                              <Button size="sm" onClick={() => handleApprove(user.id)} data-testid={`approve-${user.id}`} className="bg-accent hover:bg-accent/90 text-white rounded-full">
                                <UserCheck className="w-4 h-4 mr-1" /> Aprovar
                              </Button>
                            )}
                            {user.status === 'bloqueado_por_inatividade' && (
                              <Button size="sm" onClick={() => handleReactivate(user.id)} data-testid={`reactivate-${user.id}`} className="rounded-full">
                                Reativar
                              </Button>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
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
export default UsersPage;
