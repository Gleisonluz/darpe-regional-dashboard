import React, { useState } from 'react';
import { Sidebar } from '@/components/Sidebar';
import { TopBar } from '@/components/TopBar';
import { Button } from '@/components/ui/button';

const ReportsPage = () => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
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
            <h1 className="text-3xl font-heading font-bold text-slate-900 mb-4">Relatórios</h1>
            <p className="text-slate-600">Visualize estatísticas e relatórios da regional</p>
            <div className="mt-8 bg-white rounded-xl border border-slate-100 p-8 text-center">
              <p className="text-slate-600">Relatórios em desenvolvimento</p>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
};
export default ReportsPage;
