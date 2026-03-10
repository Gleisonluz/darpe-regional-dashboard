# DARPE Regional Itajaí - Product Requirements Document

## Resumo do Projeto
Sistema administrativo e de consulta pública para organizar e gerenciar os trabalhos de evangelização do DARPE Regional Itajaí. O sistema é responsivo (celular e desktop) e possui área pública e administrativa.

## Credenciais de Acesso
- **WhatsApp Admin:** `+5547999990001`
- **Senha:** `admin123`
- **Função:** Secretário Regional (acesso total)

## Funcionalidades Implementadas

### Área Pública (sem login)
- [x] Consulta de unidades de evangelização com filtros
- [x] Exibição de: nome, cidade, setor, tipo de serviço, frequência, horário, responsáveis

### Área Administrativa (com login)
- [x] **Autenticação:** Login com WhatsApp/celular e senha (JWT) - **SEM EMAIL**
- [x] **Perfis de Acesso:** Ancião Coordenador, Secretário Regional, Secretário Local, Atendente
- [x] **Gestão de Colaboradores:** Cadastro, listagem, aprovação (via WhatsApp)
- [x] **Gestão de Unidades:** CRUD para unidades de atendimento
- [x] **Dashboard:** Visão geral com estatísticas
- [x] **Credencial Digital:** Exibe WhatsApp, funções DARPE, cidade, localidade, QR Code

### Estrutura de Dados DARPE
- **Funções:** Atendente, Secretário Local, Secretário Regional, Ancião Coordenador
- **Tipos de Serviço:** Reunião de Evangelização, PMAE
- **Setores:** SETOR 1 a SETOR 4 (conforme especificação)

### Campos Obrigatórios do Usuário
- Nome completo
- WhatsApp/celular (único identificador de login)
- Senha
- Cidade
- Localidade
- Funções DARPE
- Status

**NOTA:** Email foi completamente removido do sistema em 10/03/2026

## Bugs Corrigidos (10/03/2026)

### 1. Erro de Runtime no UsersPage
- **Problema:** `Cannot read properties of undefined (reading 'replace')`
- **Solução:** Atualizado para usar `funcoes_darpe` com tratamento de null/undefined
- **Status:** ✅ CORRIGIDO

### 2. Bug de Persistência de Sessão
- **Problema:** Login bem-sucedido mas usuário redirecionado de volta para login
- **Solução:** Refatoração do AuthContext.js com gerenciamento de estado melhorado
- **Status:** ✅ CORRIGIDO

### 3. Remoção do Email do Sistema
- **Solicitação:** Remover email completamente do sistema DARPE
- **Ações:**
  - Backend: Removido campo email dos models.py (UserBase, UserUpdate)
  - Backend: Atualizado seed.py sem campo email
  - Backend: Atualizado fix_admin.py para usar WhatsApp
  - Frontend: Removido campo email do LoginPage.js (registro)
  - Frontend: Atualizado UserFormModal.js para usar WhatsApp
  - Frontend: Atualizado UsersPage.js para exibir apenas WhatsApp
  - Frontend: Atualizado CredentialPage.js para exibir WhatsApp e funções DARPE
  - Banco: Removido campo email de todos os documentos existentes
- **Status:** ✅ CONCLUÍDO

## Tarefas Pendentes

### P1 - Alta Prioridade
- [ ] Funcionalidade de Aprovação de Usuário (testar via UI)
- [ ] Finalizar Formulários de Admin (Unidades/Usuários)
- [ ] Implementar Gráficos nos Relatórios (Recharts)
- [ ] Finalizar Registro de Atendimento

### P2 - Média Prioridade
- [ ] Agendador da Regra de Inatividade (cron job)
- [ ] Implementar Agenda Automática
- [ ] Sistema de Notificações
- [ ] Testar Filtros da Busca Pública

## Arquitetura Técnica

### Backend (FastAPI)
```
/app/backend/
├── server.py              # Servidor principal
├── models.py              # Modelos Pydantic (sem email)
├── routes_auth_public.py  # Autenticação por WhatsApp
├── routes_admin.py        # Rotas administrativas
├── routes_features.py     # Funcionalidades
├── security.py            # JWT e autenticação
├── phone_utils.py         # Normalização de telefone
└── seed.py                # Dados iniciais
```

### Frontend (React)
```
/app/frontend/src/
├── context/AuthContext.js        # Estado de autenticação
├── components/ProtectedRoute.js  # Proteção de rotas
├── components/modals/UserFormModal.js  # Formulário de colaborador
├── pages/
│   ├── LoginPage.js      # Login/Registro por WhatsApp
│   ├── UsersPage.js      # Lista de colaboradores
│   ├── CredentialPage.js # Credencial digital
│   └── ...
```

### Banco de Dados (MongoDB)
- **users:** whatsapp (unique), nome_completo, funcoes_darpe[], cidade, localidade, status, ultimo_atendimento
- **units:** nome, cidade, setor, tipo_servico, dia_semana, horario, responsaveis[]

## Notas sobre GitHub
O projeto não possui remote Git configurado. Para salvar no GitHub:
1. Use a opção "Save to Github" na interface do chat da Emergent
2. Siga as instruções para conectar a um repositório

---
Última atualização: 10/03/2026
