import React, { useState, useEffect } from 'react';
import { Sidebar } from '@/components/Sidebar';
import { TopBar } from '@/components/TopBar';
import { unitsApi } from '@/utils/api';
import { Button } from '@/components/ui/button';
import { Plus, Church, Edit, Trash2 } from 'lucide-react';
import { UnitFormModal } from '@/components/modals/UnitFormModal';
import { toast } from 'sonner';

const UnitsPage = () => {
  const [units, setUnits] = useState([]);
  const [loading, setLoading] = useState(true);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const [editingUnit, setEditingUnit] = useState(null);

  useEffect(() => {
    loadUnits();
  }, []);

  const loadUnits = async () => {
    setLoading(true);
    try {
      const response = await unitsApi.getAll();
      setUnits(response.data);
    } catch (error) {
      console.error('Erro ao carregar unidades:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = (unit) => {
    setEditingUnit(unit);
    setModalOpen(true);
  };

  const handleDelete = async (unitId) => {
    if (!window.confirm('Tem certeza que deseja desativar esta unidade?')) return;
    
    try {
      await unitsApi.delete(unitId);
      toast.success('Unidade desativada com sucesso!');
      loadUnits();
    } catch (error) {
      toast.error('Erro ao desativar unidade');
    }
  };

  const handleCloseModal = () => {
    setModalOpen(false);
    setEditingUnit(null);
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
            <div className="flex justify-between items-center mb-8">
              <div>
                <h1 className="text-3xl font-heading font-bold text-slate-900 mb-2">Unidades de Evangelização</h1>
                <p className="text-slate-600">Gerencie as unidades da regional</p>
              </div>
              <Button data-testid="add-unit-button" onClick={() => setModalOpen(true)} className="bg-accent hover:bg-accent/90 text-white rounded-full">
                <Plus className="w-4 h-4 mr-2" /> Nova Unidade
              </Button>
            </div>

            {loading ? (
              <div className="text-center py-12">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {units.map((unit) => (
                  <div key={unit.id} data-testid={`unit-${unit.id}`} className="bg-white border border-slate-100 rounded-xl p-6 shadow-sm hover:shadow-md transition-all group">
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex items-start gap-3 flex-1">
                        <div className="w-10 h-10 bg-accent/10 rounded-lg flex items-center justify-center flex-shrink-0">
                          <Church className="w-5 h-5 text-accent" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <h3 className="font-heading font-semibold text-slate-900 truncate">{unit.nome}</h3>
                          <p className="text-sm text-slate-600">{unit.cidade}</p>
                        </div>
                      </div>
                      <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => handleEdit(unit)}
                          data-testid={`edit-unit-${unit.id}`}
                          className="h-8 w-8 p-0"
                        >
                          <Edit className="w-4 h-4 text-slate-600" />
                        </Button>
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => handleDelete(unit.id)}
                          data-testid={`delete-unit-${unit.id}`}
                          className="h-8 w-8 p-0"
                        >
                          <Trash2 className="w-4 h-4 text-red-600" />
                        </Button>
                      </div>
                    </div>
                    <div className="space-y-2 text-sm">
                      <p className="text-slate-600"><span className="font-medium">Setor:</span> <span className="text-xs">{unit.setor}</span></p>
                      <p className="text-slate-600"><span className="font-medium">Serviço:</span> {unit.tipo_servico}</p>
                      <p className="text-slate-600"><span className="font-medium">Dia:</span> <span className="capitalize">{unit.dia_semana}</span></p>
                      <p className="text-slate-600"><span className="font-medium">Horário:</span> {unit.horario}</p>
                      {unit.telefone_contato && (
                        <p className="text-slate-600"><span className="font-medium">Telefone:</span> {unit.telefone_contato}</p>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </main>
        
        <UnitFormModal
          open={modalOpen}
          onClose={handleCloseModal}
          unit={editingUnit}
          onSuccess={loadUnits}
        />
      </div>
    </div>
  );
};
export default UnitsPage;
