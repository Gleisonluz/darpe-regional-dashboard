import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Search, Filter, MapPin, Clock, Calendar, User } from 'lucide-react';
import { publicApi } from '@/utils/api';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';

const HomePage = () => {
  const [unidades, setUnidades] = useState([]);
  const [cidades, setCidades] = useState([]);
  const [filtros, setFiltros] = useState({ cidade: '', dia_semana: '', nome: '' });
  const [loading, setLoading] = useState(false);

  const diasSemana = [
    { value: 'segunda', label: 'Segunda-feira' },
    { value: 'terca', label: 'Terça-feira' },
    { value: 'quarta', label: 'Quarta-feira' },
    { value: 'quinta', label: 'Quinta-feira' },
    { value: 'sexta', label: 'Sexta-feira' },
    { value: 'sabado', label: 'Sábado' },
    { value: 'domingo', label: 'Domingo' },
  ];

  useEffect(() => {
    loadCidades();
    loadUnidades();
  }, []);

  const loadCidades = async () => {
    try {
      const response = await publicApi.getCidades();
      setCidades(response.data.cidades);
    } catch (error) {
      console.error('Erro ao carregar cidades:', error);
    }
  };

  const loadUnidades = async () => {
    setLoading(true);
    try {
      const params = {};
      if (filtros.cidade) params.cidade = filtros.cidade;
      if (filtros.dia_semana) params.dia_semana = filtros.dia_semana;
      if (filtros.nome) params.nome = filtros.nome;

      const response = await publicApi.getUnidades(params);
      setUnidades(response.data);
    } catch (error) {
      console.error('Erro ao carregar unidades:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = () => {
    loadUnidades();
  };

  return (
    <div className="min-h-screen bg-muted">
      {/* Hero Section */}
      <section className="relative bg-gradient-to-br from-slate-800 to-slate-900 text-white py-16 md:py-24">
        <div className="absolute inset-0 opacity-10">
          <div className="absolute inset-0" style={{
            backgroundImage: `url('data:image/svg+xml,%3Csvg width="60" height="60" viewBox="0 0 60 60" xmlns="http://www.w3.org/2000/svg"%3E%3Cg fill="none" fill-rule="evenodd"%3E%3Cg fill="%23ffffff" fill-opacity="0.4"%3E%3Cpath d="M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z"/%3E%3C/g%3E%3C/g%3E%3C/svg%3E')`
          }}></div>
        </div>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
          <div className="text-center">
            <h1 className="text-4xl md:text-5xl font-heading font-bold tracking-tight mb-4">
              DARPE Regional Itajaí
            </h1>
            <p className="text-lg md:text-xl text-slate-300 max-w-2xl mx-auto leading-relaxed">
              Consulte locais de evangelização, horários e responsáveis em toda a regional
            </p>
          </div>
        </div>
      </section>

      {/* Filtros */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 -mt-8 relative z-20">
        <div className="bg-white rounded-xl shadow-lg p-6 border border-slate-100">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <label className="text-sm font-medium text-slate-700 mb-2 block">Cidade</label>
              <Select value={filtros.cidade || "todos"} onValueChange={(value) => setFiltros({ ...filtros, cidade: value === "todos" ? "" : value })}>
                <SelectTrigger data-testid="filter-cidade">
                  <SelectValue placeholder="Todas as cidades" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="todos">Todas as cidades</SelectItem>
                  {cidades.map((cidade) => (
                    <SelectItem key={cidade} value={cidade}>{cidade}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div>
              <label className="text-sm font-medium text-slate-700 mb-2 block">Dia da Semana</label>
              <Select value={filtros.dia_semana || "todos"} onValueChange={(value) => setFiltros({ ...filtros, dia_semana: value === "todos" ? "" : value })}>
                <SelectTrigger data-testid="filter-dia">
                  <SelectValue placeholder="Todos os dias" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="todos">Todos os dias</SelectItem>
                  {diasSemana.map((dia) => (
                    <SelectItem key={dia.value} value={dia.value}>{dia.label}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div>
              <label className="text-sm font-medium text-slate-700 mb-2 block">Nome da Unidade</label>
              <Input
                data-testid="filter-nome"
                placeholder="Buscar por nome..."
                value={filtros.nome}
                onChange={(e) => setFiltros({ ...filtros, nome: e.target.value })}
                onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
              />
            </div>

            <div className="flex items-end">
              <Button
                data-testid="search-button"
                onClick={handleSearch}
                className="w-full bg-accent hover:bg-accent/90 text-white rounded-full"
              >
                <Search className="w-4 h-4 mr-2" />
                Buscar
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* Lista de Unidades */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {loading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
            <p className="mt-4 text-slate-600">Carregando...</p>
          </div>
        ) : unidades.length === 0 ? (
          <div className="text-center py-12 bg-white rounded-xl shadow-sm">
            <p className="text-slate-600">Nenhuma unidade encontrada com os filtros selecionados.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {unidades.map((unidade) => (
              <div
                key={unidade.id}
                data-testid={`unit-card-${unidade.id}`}
                className="bg-white border border-slate-100 rounded-xl shadow-sm hover:shadow-md hover:border-slate-200 transition-all p-6"
              >
                <h3 className="text-xl font-heading font-semibold text-slate-900 mb-3">
                  {unidade.nome}
                </h3>

                <div className="space-y-2 text-sm text-slate-600">
                  <div className="flex items-center gap-2">
                    <MapPin className="w-4 h-4 text-accent" />
                    <span>{unidade.cidade}</span>
                  </div>

                  <div className="flex items-center gap-2">
                    <Calendar className="w-4 h-4 text-accent" />
                    <span className="capitalize">{unidade.dia_semana.replace('_', '-')}</span>
                  </div>

                  <div className="flex items-center gap-2">
                    <Clock className="w-4 h-4 text-accent" />
                    <span>{unidade.horario}</span>
                  </div>

                  {unidade.tipo_atividade && (
                    <div className="mt-3 pt-3 border-t border-slate-100">
                      <span className="inline-block bg-slate-100 text-slate-700 text-xs font-medium px-3 py-1 rounded-full">
                        {unidade.tipo_atividade}
                      </span>
                    </div>
                  )}

                  {unidade.responsaveis_nomes && unidade.responsaveis_nomes.length > 0 && (
                    <div className="mt-3 pt-3 border-t border-slate-100">
                      <p className="text-xs text-slate-500 mb-1">Responsáveis:</p>
                      {unidade.responsaveis_nomes.map((nome, idx) => (
                        <div key={idx} className="flex items-center gap-2 text-sm">
                          <User className="w-3 h-3 text-slate-400" />
                          <span>{nome}</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </section>

      {/* Footer com Link para Login */}
      <footer className="bg-white border-t border-slate-200 py-8 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <p className="text-slate-600 mb-4">
            É colaborador? Acesse o sistema administrativo
          </p>
          <Link to="/login">
            <Button
              data-testid="go-to-login-button"
              className="bg-primary hover:bg-primary/90 text-white rounded-full px-8"
            >
              Fazer Login
            </Button>
          </Link>
        </div>
      </footer>
    </div>
  );
};

export default HomePage;
