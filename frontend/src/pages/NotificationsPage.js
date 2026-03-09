import React, { useState, useEffect } from 'react';
import { Sidebar } from '@/components/Sidebar';
import { TopBar } from '@/components/TopBar';
import { notificationsApi } from '@/utils/api';
import { Button } from '@/components/ui/button';
import { CheckCheck, Bell } from 'lucide-react';
import { toast } from 'sonner';

const NotificationsPage = () => {
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  useEffect(() => {
    loadNotifications();
  }, []);

  const loadNotifications = async () => {
    try {
      const response = await notificationsApi.getAll();
      setNotifications(response.data);
    } catch (error) {
      console.error('Erro ao carregar notificações:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleMarkAllAsRead = async () => {
    try {
      await notificationsApi.markAllAsRead();
      toast.success('Todas marcadas como lidas');
      loadNotifications();
    } catch (error) {
      toast.error('Erro ao marcar notificações');
    }
  };

  const handleMarkAsRead = async (id) => {
    try {
      await notificationsApi.markAsRead(id);
      loadNotifications();
    } catch (error) {
      console.error('Erro ao marcar como lida:', error);
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleString('pt-BR');
  };

  const getTypeIcon = (tipo) => {
    return <Bell className="w-5 h-5" />;
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
          <div className="max-w-4xl mx-auto">
            <div className="flex justify-between items-center mb-8">
              <div>
                <h1 className="text-3xl font-heading font-bold text-slate-900 mb-2">Notificações</h1>
                <p className="text-slate-600">Acompanhe seus avisos e atualizações</p>
              </div>
              <Button data-testid="mark-all-read" onClick={handleMarkAllAsRead} className="rounded-full">
                <CheckCheck className="w-4 h-4 mr-2" /> Marcar todas como lidas
              </Button>
            </div>

            {loading ? (
              <div className="text-center py-12">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
              </div>
            ) : notifications.length === 0 ? (
              <div className="bg-white rounded-xl border border-slate-100 p-12 text-center">
                <Bell className="w-16 h-16 text-slate-300 mx-auto mb-4" />
                <p className="text-slate-600">Nenhuma notificação</p>
              </div>
            ) : (
              <div className="space-y-3">
                {notifications.map((notif) => (
                  <div
                    key={notif.id}
                    data-testid={`notification-${notif.id}`}
                    onClick={() => !notif.lida && handleMarkAsRead(notif.id)}
                    className={`bg-white border rounded-xl p-4 cursor-pointer transition-all ${
                      notif.lida ? 'border-slate-100' : 'border-accent bg-accent/5'
                    }`}
                  >
                    <div className="flex gap-4">
                      <div className={`w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0 ${
                        notif.tipo === 'success' ? 'bg-emerald-50 text-emerald-600' : 
                        notif.tipo === 'warning' ? 'bg-amber-50 text-amber-600' : 
                        'bg-accent/10 text-accent'
                      }`}>
                        {getTypeIcon(notif.tipo)}
                      </div>
                      <div className="flex-1">
                        <div className="flex justify-between items-start mb-1">
                          <h3 className="font-medium text-slate-900">{notif.titulo}</h3>
                          {!notif.lida && <span className="w-2 h-2 bg-accent rounded-full flex-shrink-0"></span>}
                        </div>
                        <p className="text-sm text-slate-600 mb-2">{notif.mensagem}</p>
                        <p className="text-xs text-slate-400">{formatDate(notif.created_at)}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </main>
      </div>
    </div>
  );
};
export default NotificationsPage;
