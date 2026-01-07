# Funcionalidades Financeiras Mensais - ERP Pessoal

## Visão Geral

Implementação completa de todos os fluxos financeiros de forma mensal, proporcionando uma visão consolidada e análise detalhada das finanças pessoais por período mensal.

## 🚀 Novas Funcionalidades Implementadas

### 1. Relatórios Financeiros Mensais Automáticos

#### Endpoints Disponíveis:
- `GET /api/financeiro/relatorios/mensal` - Relatório completo do mês
- `GET /api/financeiro/relatorios/fluxo-caixa-mensal` - Análise de fluxo de caixa
- `GET /api/financeiro/relatorios/comparativo-mensal` - Comparação com mês anterior
- `GET /api/financeiro/relatorios/alertas-mensais` - Alertas e notificações
- `POST /api/financeiro/relatorios/gerar-resumo-mensal` - Gerar resumo automático

#### Funcionalidades:
- ✅ Análise completa de receitas e despesas por mês
- ✅ Cálculo automático de saldo mensal
- ✅ Relatórios por categoria (receitas e despesas)
- ✅ Contagem de contas pagas e vencidas
- ✅ Acompanhamento de metas concluídas e ativas
- ✅ Geração automática de resumos financeiros

### 2. Sistema de Metas Mensais Automáticas

#### Endpoints Disponíveis:
- `POST /api/financeiro/metas-mensais` - Criar meta mensal
- `GET /api/financeiro/metas-mensais` - Listar metas mensais
- `GET /api/financeiro/metas-mensais/{id}` - Obter meta específica
- `PUT /api/financeiro/metas-mensais/{id}` - Atualizar meta
- `DELETE /api/financeiro/metas-mensais/{id}` - Deletar meta

#### Funcionalidades:
- ✅ Definição de metas para receitas, despesas, investimentos e poupança
- ✅ Cálculo automático de percentuais de realização
- ✅ Status geral da meta (excelente, bom, regular, ruim)
- ✅ Atualização automática dos valores realizados
- ✅ Histórico completo de metas mensais

### 3. Dashboard Mensal Consolidado

#### Endpoint:
- `GET /api/financeiro/dashboard-mensal` - Dashboard completo do mês
- `GET /dashboard-mensal` - Interface web do dashboard

#### Funcionalidades:
- ✅ Visão consolidada de todos os dados mensais
- ✅ Gráficos interativos de receitas e despesas por categoria
- ✅ Barras de progresso das metas mensais
- ✅ Alertas e notificações em tempo real
- ✅ Próximos vencimentos e metas
- ✅ Navegação entre meses (anterior/próximo)

### 4. Análise de Fluxo de Caixa Mensal

#### Funcionalidades:
- ✅ Cálculo de saldo inicial do mês
- ✅ Entradas e saídas do período
- ✅ Saldo final e variação mensal
- ✅ Percentual de variação
- ✅ Histórico acumulado por mês

### 5. Comparativo Mensal

#### Funcionalidades:
- ✅ Comparação automática com mês anterior
- ✅ Cálculo de variações (receitas, despesas, saldo)
- ✅ Determinação de tendência (crescimento, declínio, estável)
- ✅ Análise de evolução financeira

### 6. Sistema de Alertas e Notificações

#### Funcionalidades:
- ✅ Detecção de contas vencidas
- ✅ Identificação de metas atrasadas
- ✅ Alertas de investimentos com rentabilidade negativa
- ✅ Notificação de saldo negativo
- ✅ Alertas críticos personalizados

### 7. Exportação de Relatórios

#### Endpoints:
- `GET /api/financeiro/relatorios/exportar-mensal` - Exportar em JSON/CSV
- `POST /api/financeiro/relatorios/gerar-todos-meses` - Gerar relatórios do ano

#### Funcionalidades:
- ✅ Exportação em formato JSON
- ✅ Exportação em formato CSV
- ✅ Geração automática de relatórios para todo o ano
- ✅ Dados completos para análise externa

## 📊 Estrutura de Dados

### Nova Tabela: `metas_mensais`
```sql
CREATE TABLE metas_mensais (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    mes INTEGER NOT NULL,
    ano INTEGER NOT NULL,
    meta_receita FLOAT NOT NULL,
    meta_despesa FLOAT NOT NULL,
    meta_investimento FLOAT NOT NULL,
    meta_poupanca FLOAT NOT NULL,
    receita_realizada FLOAT DEFAULT 0.0,
    despesa_realizada FLOAT DEFAULT 0.0,
    investimento_realizado FLOAT DEFAULT 0.0,
    poupanca_realizada FLOAT DEFAULT 0.0,
    percentual_receita FLOAT DEFAULT 0.0,
    percentual_despesa FLOAT DEFAULT 0.0,
    percentual_investimento FLOAT DEFAULT 0.0,
    percentual_poupanca FLOAT DEFAULT 0.0,
    status_geral VARCHAR DEFAULT 'regular',
    observacoes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);
```

## 🎯 Como Usar

### 1. Acessar Dashboard Mensal
```
http://localhost:8000/dashboard-mensal
```

### 2. Criar Meta Mensal
```bash
curl -X POST "http://localhost:8000/api/financeiro/metas-mensais" \
  -H "Authorization: Bearer SEU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "mes": 12,
    "ano": 2024,
    "meta_receita": 5000.0,
    "meta_despesa": 3000.0,
    "meta_investimento": 1000.0,
    "meta_poupanca": 500.0
  }'
```

### 3. Obter Relatório Mensal
```bash
curl -X GET "http://localhost:8000/api/financeiro/relatorios/mensal?mes=12&ano=2024" \
  -H "Authorization: Bearer SEU_TOKEN"
```

### 4. Exportar Relatório
```bash
# JSON
curl -X GET "http://localhost:8000/api/financeiro/relatorios/exportar-mensal?mes=12&ano=2024&formato=json" \
  -H "Authorization: Bearer SEU_TOKEN"

# CSV
curl -X GET "http://localhost:8000/api/financeiro/relatorios/exportar-mensal?mes=12&ano=2024&formato=csv" \
  -H "Authorization: Bearer SEU_TOKEN"
```

## 📈 Benefícios

### Para o Usuário:
- ✅ **Visão Consolidada**: Dashboard único com todos os dados mensais
- ✅ **Análise Detalhada**: Relatórios completos por categoria e período
- ✅ **Metas Inteligentes**: Sistema automático de acompanhamento de objetivos
- ✅ **Alertas Proativos**: Notificações para evitar problemas financeiros
- ✅ **Exportação Fácil**: Relatórios em múltiplos formatos
- ✅ **Navegação Intuitiva**: Interface amigável para análise temporal

### Para o Sistema:
- ✅ **Performance**: Consultas otimizadas para análise mensal
- ✅ **Escalabilidade**: Estrutura preparada para grandes volumes de dados
- ✅ **Flexibilidade**: APIs RESTful para integração externa
- ✅ **Manutenibilidade**: Código bem estruturado e documentado

## 🔧 Configuração e Instalação

### 1. Atualizar Banco de Dados
```bash
python3 update_database_mensal.py
```

### 2. Reiniciar Servidor
```bash
python3 main.py
```

### 3. Acessar Funcionalidades
- Dashboard Mensal: `http://localhost:8000/dashboard-mensal`
- API Docs: `http://localhost:8000/docs`

## 📋 Próximos Passos

### Funcionalidades Futuras:
- [ ] Relatórios trimestrais e anuais
- [ ] Previsões financeiras baseadas em histórico
- [ ] Integração com APIs bancárias
- [ ] Notificações por email/SMS
- [ ] Relatórios personalizados
- [ ] Análise de tendências avançada

## 🎉 Conclusão

O sistema agora oferece uma visão completa e mensal de todas as finanças pessoais, com:

- **8 novos endpoints** para análise mensal
- **1 nova tabela** para metas mensais
- **1 dashboard** interativo e responsivo
- **Exportação** em múltiplos formatos
- **Alertas** inteligentes e proativos
- **Metas** automáticas e acompanhamento

Todos os fluxos financeiros agora funcionam de forma mensal, proporcionando controle total sobre as finanças pessoais! 🚀

