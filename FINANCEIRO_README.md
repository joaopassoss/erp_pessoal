# Módulo Financeiro - ERP Pessoal

## Visão Geral

O módulo financeiro é um sistema completo de controle financeiro pessoal desenvolvido para gerenciar suas finanças domésticas. Ele oferece funcionalidades abrangentes para controle de receitas, despesas, metas financeiras e investimentos.

## Funcionalidades Principais

### 1. Contas a Pagar
- **Cadastro de contas**: Registre todas as suas despesas com descrição, valor, data de vencimento e categoria
- **Categorização**: Organize por categorias (Alimentação, Transporte, Moradia, Saúde, Educação, Lazer, Outros)
- **Controle de status**: Pendente, Pago, Vencido, Cancelado
- **Filtros avançados**: Por status, categoria, mês e ano
- **Marcação de pagamento**: Marque contas como pagas com data específica

### 2. Contas a Receber
- **Controle de receitas**: Registre salários, vendas, aluguéis e outras receitas
- **Mesma estrutura**: Categorização e filtros similares às contas a pagar
- **Status de recebimento**: Controle se a receita já foi recebida

### 3. Metas Financeiras
- **Criação de metas**: Defina objetivos financeiros com valor e prazo
- **Acompanhamento visual**: Barra de progresso e percentual de conclusão
- **Histórico de transações**: Registre cada valor destinado à meta
- **Status inteligente**: Meta é marcada como concluída automaticamente
- **Cores personalizáveis**: Identifique metas visualmente

### 4. Investimentos
- **Diversos tipos**: Poupança, CDB, LCI, LCA, Fundos, Ações, Cripto, Outros
- **Controle de rentabilidade**: Acompanhe valor investido vs valor atual
- **Cálculo automático**: Percentual de rentabilidade calculado automaticamente
- **Status ativo/inativo**: Controle investimentos ativos e finalizados

### 5. Dashboard e Relatórios
- **Visão geral**: Saldo atual, receitas e despesas do mês
- **Gráficos interativos**: Evolução financeira dos últimos 12 meses
- **Relatórios por categoria**: Análise de gastos e receitas por categoria
- **Próximas contas**: Lista de contas que vencem nos próximos 7 dias
- **Metas próximas**: Metas que vencem nos próximos 30 dias

## Estrutura Técnica

### Modelos de Dados
- **ContaPagar**: Contas a pagar com categorização e status
- **ContaReceber**: Contas a receber com categorização e status
- **MetaFinanceira**: Metas com progresso e status
- **TransacaoMeta**: Histórico de valores destinados às metas
- **Investimento**: Investimentos com rentabilidade
- **ResumoFinanceiro**: Dados agregados para relatórios

### APIs Disponíveis

#### Contas a Pagar
- `POST /api/financeiro/contas-pagar` - Criar conta
- `GET /api/financeiro/contas-pagar` - Listar contas (com filtros)
- `GET /api/financeiro/contas-pagar/{id}` - Obter conta específica
- `PUT /api/financeiro/contas-pagar/{id}` - Atualizar conta
- `DELETE /api/financeiro/contas-pagar/{id}` - Deletar conta
- `POST /api/financeiro/contas-pagar/{id}/pagar` - Marcar como pago

#### Contas a Receber
- `POST /api/financeiro/contas-receber` - Criar conta
- `GET /api/financeiro/contas-receber` - Listar contas (com filtros)
- `GET /api/financeiro/contas-receber/{id}` - Obter conta específica
- `PUT /api/financeiro/contas-receber/{id}` - Atualizar conta
- `DELETE /api/financeiro/contas-receber/{id}` - Deletar conta
- `POST /api/financeiro/contas-receber/{id}/receber` - Marcar como recebido

#### Metas Financeiras
- `POST /api/financeiro/metas` - Criar meta
- `GET /api/financeiro/metas` - Listar metas (com filtros)
- `GET /api/financeiro/metas/{id}` - Obter meta específica
- `PUT /api/financeiro/metas/{id}` - Atualizar meta
- `DELETE /api/financeiro/metas/{id}` - Deletar meta
- `POST /api/financeiro/metas/{id}/transacoes` - Adicionar valor à meta
- `GET /api/financeiro/metas/{id}/transacoes` - Listar transações da meta

#### Investimentos
- `POST /api/financeiro/investimentos` - Criar investimento
- `GET /api/financeiro/investimentos` - Listar investimentos (com filtros)
- `GET /api/financeiro/investimentos/{id}` - Obter investimento específico
- `PUT /api/financeiro/investimentos/{id}` - Atualizar investimento
- `DELETE /api/financeiro/investimentos/{id}` - Deletar investimento

#### Dashboard e Relatórios
- `GET /api/financeiro/dashboard` - Dados do dashboard
- `GET /api/financeiro/graficos/mensal` - Gráfico de evolução mensal
- `GET /api/financeiro/relatorios/categorias` - Relatório por categorias

## Como Usar

### 1. Acesso ao Módulo
- Faça login no sistema
- No dashboard, clique em "Módulo Financeiro"
- Ou acesse diretamente `/financeiro`

### 2. Primeiros Passos
1. **Configure suas contas a pagar**: Registre suas despesas fixas e variáveis
2. **Cadastre suas receitas**: Inclua salário e outras fontes de renda
3. **Crie suas metas**: Defina objetivos financeiros com prazos
4. **Registre investimentos**: Adicione seus investimentos atuais

### 3. Uso Diário
- **Controle de fluxo**: Use as contas a pagar/receber para controle diário
- **Acompanhamento de metas**: Adicione valores regularmente às suas metas
- **Análise de gastos**: Use os relatórios para entender seus padrões de gasto
- **Monitoramento**: Acompanhe o dashboard para visão geral da situação

## Categorias Disponíveis

### Despesas e Receitas
- **Alimentação**: Supermercado, restaurantes, delivery
- **Transporte**: Combustível, transporte público, manutenção
- **Moradia**: Aluguel, condomínio, IPTU, manutenção
- **Saúde**: Médicos, medicamentos, planos de saúde
- **Educação**: Cursos, livros, mensalidades
- **Lazer**: Cinema, viagens, hobbies
- **Outros**: Categorias não especificadas

### Tipos de Investimento
- **Poupança**: Conta poupança tradicional
- **CDB**: Certificado de Depósito Bancário
- **LCI**: Letra de Crédito Imobiliário
- **LCA**: Letra de Crédito do Agronegócio
- **Fundos**: Fundos de investimento
- **Ações**: Ações na bolsa de valores
- **Cripto**: Criptomoedas
- **Outros**: Outros tipos de investimento

## Recursos Avançados

### Filtros Inteligentes
- Filtre contas por status, categoria, mês e ano
- Visualize apenas dados relevantes para sua análise

### Gráficos Interativos
- Gráfico de linha mostrando evolução financeira
- Gráficos de pizza para análise de categorias
- Dados atualizados em tempo real

### Responsividade
- Interface adaptada para desktop, tablet e mobile
- Navegação intuitiva e fácil de usar

## Segurança

- **Autenticação obrigatória**: Todas as operações requerem login
- **Isolamento de dados**: Cada usuário vê apenas seus próprios dados
- **Validação de dados**: Todos os dados são validados antes de serem salvos
- **Transações seguras**: Operações de banco de dados são transacionais

## Próximas Funcionalidades

- [ ] Importação de extratos bancários
- [ ] Planejamento de orçamento mensal
- [ ] Alertas de vencimento por email
- [ ] Relatórios em PDF
- [ ] Integração com APIs de investimentos
- [ ] Categorização automática de transações
- [ ] Metas com parcelas mensais
- [ ] Análise de tendências financeiras

## Suporte

Para dúvidas ou problemas com o módulo financeiro:
1. Verifique se todas as dependências estão instaladas
2. Confirme se o banco de dados foi atualizado
3. Verifique os logs do sistema para erros
4. Consulte a documentação da API em `/docs`

---

**Desenvolvido para controle financeiro pessoal e doméstico** 🏠💰

