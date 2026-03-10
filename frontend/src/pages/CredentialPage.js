import React, { useState, useEffect } from 'react';
import { Sidebar } from '@/components/Sidebar';
import { TopBar } from '@/components/TopBar';
import { credentialApi, uploadApi } from '@/utils/api';
import { Upload, CheckCircle, XCircle, Camera } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { toast } from 'sonner';

const CredentialPage = () => {
  const [credential, setCredential] = useState(null);
  const [loading, setLoading] = useState(true);
  const [uploadingPhoto, setUploadingPhoto] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  useEffect(() => {
    loadCredential();
  }, []);

  const loadCredential = async () => {
    setLoading(true);
    try {
      const response = await credentialApi.get();
      setCredential(response.data);
    } catch (error) {
      console.error('Erro ao carregar credencial:', error);
      toast.error(error.response?.data?.detail || 'Erro ao carregar credencial');
    } finally {
      setLoading(false);
    }
  };

  const handlePhotoUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    // Validar tipo
    if (!file.type.startsWith('image/')) {
      toast.error('Por favor, selecione uma imagem');
      return;
    }

    // Validar tamanho (5MB)
    if (file.size > 5 * 1024 * 1024) {
      toast.error('A imagem deve ter no máximo 5MB');
      return;
    }

    setUploadingPhoto(true);
    try {
      await uploadApi.uploadPhoto(file);
      toast.success('Foto atualizada com sucesso!');
      loadCredential();
    } catch (error) {
      console.error('Erro ao fazer upload:', error);
      toast.error('Erro ao enviar foto');
    } finally {
      setUploadingPhoto(false);
    }
  };

  const getStatusConfig = (status) => {
    const configs = {
      ativo: { label: 'ATIVO', color: 'bg-emerald-50 text-emerald-700 border-emerald-200' },
      bloqueado_por_inatividade: { label: 'BLOQUEADO', color: 'bg-red-50 text-red-700 border-red-200' },
      inativo: { label: 'INATIVO', color: 'bg-slate-100 text-slate-600 border-slate-200' },
      pendente: { label: 'PENDENTE', color: 'bg-amber-50 text-amber-700 border-amber-200' }
    };
    return configs[status] || configs.inativo;
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'Nunca';
    const date = new Date(dateString);
    return date.toLocaleDateString('pt-BR');
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
                Minha Credencial Digital
              </h1>
              <p className="text-slate-600">
                Apresente esta credencial ao visitar uma unidade de evangelização
              </p>
            </div>

            {loading ? (
              <div className="text-center py-12">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
                <p className="mt-4 text-slate-600">Carregando credencial...</p>
              </div>
            ) : credential ? (
              <div className="space-y-8">
                {/* Credencial Digital */}
                <div
                  data-testid="digital-credential"
                  className="bg-white border-2 border-slate-200 rounded-2xl shadow-lg overflow-hidden max-w-md mx-auto"
                  style={{
                    background: 'linear-gradient(135deg, #ffffff 0%, #f8fafc 100%)'
                  }}
                >
                  {/* Header com padrão */}
                  <div className="relative bg-gradient-to-br from-slate-800 to-slate-900 p-6">
                    <div className="absolute inset-0 opacity-10">
                      <div className="absolute inset-0" style={{
                        backgroundImage: `url('data:image/svg+xml,%3Csvg width="40" height="40" viewBox="0 0 40 40" xmlns="http://www.w3.org/2000/svg"%3E%3Cg fill="%23ffffff" fill-opacity="0.4"%3E%3Cpath d="M0 0h20v20H0V0zm10 17a7 7 0 1 0 0-14 7 7 0 0 0 0 14zm20 0a7 7 0 1 0 0-14 7 7 0 0 0 0 14zM10 37a7 7 0 1 0 0-14 7 7 0 0 0 0 14zm10-17a7 7 0 1 0 0-14 7 7 0 0 0 0 14zm10 17a7 7 0 1 0 0-14 7 7 0 0 0 0 14z"/%3E%3C/g%3E%3C/svg%3E')`
                      }}></div>
                    </div>
                    <div className="relative z-10">
                      <p className="text-white text-sm font-medium mb-1">DARPE Regional Itajaí</p>
                      <p className="text-slate-300 text-xs">Credencial de Atendente</p>
                    </div>
                  </div>

                  {/* Foto e Informações */}
                  <div className="p-6">
                    <div className="flex flex-col items-center mb-6">
                      <div className="relative mb-4">
                        <div className="w-32 h-32 rounded-full overflow-hidden bg-slate-200 border-4 border-white shadow-lg">
                          {credential.user.foto_url ? (
                            <img
                              src={credential.user.foto_url}
                              alt={credential.user.nome_completo}
                              className="w-full h-full object-cover"
                            />
                          ) : (
                            <div className="w-full h-full flex items-center justify-center bg-accent text-white text-4xl font-bold">
                              {credential.user.nome_completo.charAt(0)}
                            </div>
                          )}
                        </div>
                        <label className="absolute bottom-0 right-0 w-10 h-10 bg-accent rounded-full flex items-center justify-center text-white cursor-pointer hover:bg-accent/90 shadow-lg transition-colors">
                          <input
                            type="file"
                            accept="image/*"
                            className="hidden"
                            onChange={handlePhotoUpload}
                            disabled={uploadingPhoto}
                          />
                          {uploadingPhoto ? (
                            <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                          ) : (
                            <Camera className="w-5 h-5" />
                          )}
                        </label>
                      </div>

                      <h2 className="text-2xl font-heading font-bold text-slate-900 text-center mb-1">
                        {credential.user.nome_completo}
                      </h2>
                      
                      <div className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-full border text-xs font-semibold uppercase tracking-wider ${getStatusConfig(credential.user.status).color}`}>
                        {credential.user.status === 'ativo' ? (
                          <CheckCircle className="w-4 h-4" />
                        ) : (
                          <XCircle className="w-4 h-4" />
                        )}
                        {getStatusConfig(credential.user.status).label}
                      </div>
                    </div>

                    {/* Informações */}
                    <div className="space-y-3 mb-6">
                      <div className="flex justify-between py-2 border-b border-slate-100">
                        <span className="text-sm text-slate-600">WhatsApp:</span>
                        <span className="text-sm font-medium text-slate-900">
                          {credential.user.whatsapp || 'Não informado'}
                        </span>
                      </div>

                      <div className="py-2 border-b border-slate-100">
                        <span className="text-sm text-slate-600 block mb-2">Funções DARPE:</span>
                        <div className="flex flex-wrap gap-1">
                          {credential.user.funcoes_darpe && credential.user.funcoes_darpe.length > 0 ? (
                            credential.user.funcoes_darpe.map((funcao, idx) => (
                              <span key={idx} className="text-xs bg-accent/10 text-accent px-2 py-1 rounded-full">
                                {funcao}
                              </span>
                            ))
                          ) : (
                            <span className="text-sm text-slate-500">Atendente</span>
                          )}
                        </div>
                      </div>
                      
                      {credential.user.cidade && (
                        <div className="flex justify-between py-2 border-b border-slate-100">
                          <span className="text-sm text-slate-600">Cidade:</span>
                          <span className="text-sm font-medium text-slate-900">{credential.user.cidade}</span>
                        </div>
                      )}

                      {credential.user.localidade && (
                        <div className="flex justify-between py-2 border-b border-slate-100">
                          <span className="text-sm text-slate-600">Localidade:</span>
                          <span className="text-sm font-medium text-slate-900">{credential.user.localidade}</span>
                        </div>
                      )}

                      <div className="flex justify-between py-2 border-b border-slate-100">
                        <span className="text-sm text-slate-600">Último Atendimento:</span>
                        <span className="text-sm font-medium text-slate-900">
                          {formatDate(credential.user.ultimo_atendimento)}
                        </span>
                      </div>

                      {credential.unidades.length > 0 && (
                        <div className="py-2">
                          <p className="text-sm text-slate-600 mb-2">Unidades que atende:</p>
                          <div className="space-y-1">
                            {credential.unidades.map((unidade) => (
                              <div key={unidade.id} className="text-sm font-medium text-slate-900 bg-slate-50 px-3 py-2 rounded-lg">
                                {unidade.nome} - {unidade.cidade}
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>

                    {/* QR Code */}
                    <div className="bg-slate-50 rounded-xl p-6 text-center">
                      <p className="text-xs text-slate-500 mb-3 uppercase tracking-wider font-semibold">
                        Código de Validação
                      </p>
                      <div className="inline-block bg-white p-4 rounded-lg shadow-sm">
                        <img
                          src={credential.qr_code}
                          alt="QR Code"
                          className="w-48 h-48 mx-auto"
                        />
                      </div>
                      <p className="text-xs text-slate-500 mt-3">
                        ID: {credential.user.id.substring(0, 8)}
                      </p>
                    </div>
                  </div>
                </div>

                {/* Instruções */}
                <div className="bg-white rounded-xl border border-slate-100 p-6 shadow-sm">
                  <h3 className="text-lg font-heading font-semibold text-slate-900 mb-4">
                    Como usar sua credencial
                  </h3>
                  <ul className="space-y-3 text-slate-600">
                    <li className="flex items-start gap-3">
                      <div className="w-6 h-6 bg-accent/10 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                        <span className="text-xs font-bold text-accent">1</span>
                      </div>
                      <span>Mantenha sua credencial sempre atualizada com uma foto recente</span>
                    </li>
                    <li className="flex items-start gap-3">
                      <div className="w-6 h-6 bg-accent/10 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                        <span className="text-xs font-bold text-accent">2</span>
                      </div>
                      <span>Apresente o QR code ao responsável da unidade ao chegar</span>
                    </li>
                    <li className="flex items-start gap-3">
                      <div className="w-6 h-6 bg-accent/10 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                        <span className="text-xs font-bold text-accent">3</span>
                      </div>
                      <span>Registre sua presença a cada atendimento para manter sua credencial ativa</span>
                    </li>
                    <li className="flex items-start gap-3">
                      <div className="w-6 h-6 bg-accent/10 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                        <span className="text-xs font-bold text-accent">4</span>
                      </div>
                      <span>Se ficar mais de 90 dias sem registrar presença, sua credencial será bloqueada automaticamente</span>
                    </li>
                  </ul>
                </div>
              </div>
            ) : (
              <div className="text-center py-12 bg-white rounded-xl shadow-sm">
                <XCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
                <p className="text-slate-600">Não foi possível carregar sua credencial</p>
              </div>
            )}
          </div>
        </main>
      </div>
    </div>
  );
};

export default CredentialPage;
