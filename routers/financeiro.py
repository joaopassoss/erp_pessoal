from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from database import get_db
from models import (
    User, ContaPagar, ContaReceber, MetaFinanceira, TransacaoMeta, 
    Investimento, ResumoFinanceiro, CategoriaConta, StatusConta, 
    TipoInvestimento, StatusMeta
)
from schemas import (
    ContaPagarCreate, ContaPagarUpdate, ContaPagarResponse,
    ContaReceberCreate, ContaReceberUpdate, ContaReceberResponse,
    MetaFinanceiraCreate, MetaFinanceiraUpdate, MetaFinanceiraResponse,
    TransacaoMetaCreate, TransacaoMetaResponse,
    InvestimentoCreate, InvestimentoUpdate, InvestimentoResponse,
    DashboardResponse, GraficoMensalResponse, RelatorioCategoriaResponse
)
from auth import get_current_user
from typing import List, Optional
from datetime import datetime, date, timedelta
import calendar

router = APIRouter(prefix="/financeiro", tags=["Financeiro"])

# ==================== CONTAS A PAGAR ====================

@router.post("/contas-pagar", response_model=ContaPagarResponse)
def criar_conta_pagar(
    conta: ContaPagarCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Criar nova conta a pagar"""
    db_conta = ContaPagar(
        user_id=current_user.id,
        **conta.dict()
    )
    db.add(db_conta)
    db.commit()
    db.refresh(db_conta)
    return db_conta

@router.get("/contas-pagar", response_model=List[ContaPagarResponse])
def listar_contas_pagar(
    status: Optional[StatusConta] = None,
    categoria: Optional[CategoriaConta] = None,
    mes: Optional[int] = None,
    ano: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Listar contas a pagar com filtros"""
    query = db.query(ContaPagar).filter(ContaPagar.user_id == current_user.id)
    
    if status:
        query = query.filter(ContaPagar.status == status)
    if categoria:
        query = query.filter(ContaPagar.categoria == categoria)
    if mes and ano:
        query = query.filter(
            func.extract('month', ContaPagar.data_vencimento) == mes,
            func.extract('year', ContaPagar.data_vencimento) == ano
        )
    
    return query.order_by(ContaPagar.data_vencimento).all()

@router.get("/contas-pagar/{conta_id}", response_model=ContaPagarResponse)
def obter_conta_pagar(
    conta_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obter conta a pagar específica"""
    conta = db.query(ContaPagar).filter(
        ContaPagar.id == conta_id,
        ContaPagar.user_id == current_user.id
    ).first()
    
    if not conta:
        raise HTTPException(status_code=404, detail="Conta não encontrada")
    
    return conta

@router.put("/contas-pagar/{conta_id}", response_model=ContaPagarResponse)
def atualizar_conta_pagar(
    conta_id: int,
    conta_update: ContaPagarUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Atualizar conta a pagar"""
    conta = db.query(ContaPagar).filter(
        ContaPagar.id == conta_id,
        ContaPagar.user_id == current_user.id
    ).first()
    
    if not conta:
        raise HTTPException(status_code=404, detail="Conta não encontrada")
    
    for field, value in conta_update.dict(exclude_unset=True).items():
        setattr(conta, field, value)
    
    db.commit()
    db.refresh(conta)
    return conta

@router.delete("/contas-pagar/{conta_id}")
def deletar_conta_pagar(
    conta_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Deletar conta a pagar"""
    conta = db.query(ContaPagar).filter(
        ContaPagar.id == conta_id,
        ContaPagar.user_id == current_user.id
    ).first()
    
    if not conta:
        raise HTTPException(status_code=404, detail="Conta não encontrada")
    
    db.delete(conta)
    db.commit()
    return {"message": "Conta deletada com sucesso"}

@router.post("/contas-pagar/{conta_id}/pagar")
def marcar_como_pago(
    conta_id: int,
    data_pagamento: Optional[date] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Marcar conta como paga"""
    conta = db.query(ContaPagar).filter(
        ContaPagar.id == conta_id,
        ContaPagar.user_id == current_user.id
    ).first()
    
    if not conta:
        raise HTTPException(status_code=404, detail="Conta não encontrada")
    
    conta.status = StatusConta.PAGO
    conta.data_pagamento = data_pagamento or date.today()
    
    db.commit()
    return {"message": "Conta marcada como paga"}

# ==================== CONTAS A RECEBER ====================

@router.post("/contas-receber", response_model=ContaReceberResponse)
def criar_conta_receber(
    conta: ContaReceberCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Criar nova conta a receber"""
    db_conta = ContaReceber(
        user_id=current_user.id,
        **conta.dict()
    )
    db.add(db_conta)
    db.commit()
    db.refresh(db_conta)
    return db_conta

@router.get("/contas-receber", response_model=List[ContaReceberResponse])
def listar_contas_receber(
    status: Optional[StatusConta] = None,
    categoria: Optional[CategoriaConta] = None,
    mes: Optional[int] = None,
    ano: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Listar contas a receber com filtros"""
    query = db.query(ContaReceber).filter(ContaReceber.user_id == current_user.id)
    
    if status:
        query = query.filter(ContaReceber.status == status)
    if categoria:
        query = query.filter(ContaReceber.categoria == categoria)
    if mes and ano:
        query = query.filter(
            func.extract('month', ContaReceber.data_vencimento) == mes,
            func.extract('year', ContaReceber.data_vencimento) == ano
        )
    
    return query.order_by(ContaReceber.data_vencimento).all()

@router.get("/contas-receber/{conta_id}", response_model=ContaReceberResponse)
def obter_conta_receber(
    conta_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obter conta a receber específica"""
    conta = db.query(ContaReceber).filter(
        ContaReceber.id == conta_id,
        ContaReceber.user_id == current_user.id
    ).first()
    
    if not conta:
        raise HTTPException(status_code=404, detail="Conta não encontrada")
    
    return conta

@router.put("/contas-receber/{conta_id}", response_model=ContaReceberResponse)
def atualizar_conta_receber(
    conta_id: int,
    conta_update: ContaReceberUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Atualizar conta a receber"""
    conta = db.query(ContaReceber).filter(
        ContaReceber.id == conta_id,
        ContaReceber.user_id == current_user.id
    ).first()
    
    if not conta:
        raise HTTPException(status_code=404, detail="Conta não encontrada")
    
    for field, value in conta_update.dict(exclude_unset=True).items():
        setattr(conta, field, value)
    
    db.commit()
    db.refresh(conta)
    return conta

@router.delete("/contas-receber/{conta_id}")
def deletar_conta_receber(
    conta_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Deletar conta a receber"""
    conta = db.query(ContaReceber).filter(
        ContaReceber.id == conta_id,
        ContaReceber.user_id == current_user.id
    ).first()
    
    if not conta:
        raise HTTPException(status_code=404, detail="Conta não encontrada")
    
    db.delete(conta)
    db.commit()
    return {"message": "Conta deletada com sucesso"}

@router.post("/contas-receber/{conta_id}/receber")
def marcar_como_recebido(
    conta_id: int,
    data_recebimento: Optional[date] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Marcar conta como recebida"""
    conta = db.query(ContaReceber).filter(
        ContaReceber.id == conta_id,
        ContaReceber.user_id == current_user.id
    ).first()
    
    if not conta:
        raise HTTPException(status_code=404, detail="Conta não encontrada")
    
    conta.status = StatusConta.PAGO
    conta.data_recebimento = data_recebimento or date.today()
    
    db.commit()
    return {"message": "Conta marcada como recebida"}

# ==================== METAS FINANCEIRAS ====================

@router.post("/metas", response_model=MetaFinanceiraResponse)
def criar_meta_financeira(
    meta: MetaFinanceiraCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Criar nova meta financeira"""
    db_meta = MetaFinanceira(
        user_id=current_user.id,
        **meta.dict()
    )
    db.add(db_meta)
    db.commit()
    db.refresh(db_meta)
    return db_meta

@router.get("/metas", response_model=List[MetaFinanceiraResponse])
def listar_metas_financeiras(
    status: Optional[StatusMeta] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Listar metas financeiras"""
    query = db.query(MetaFinanceira).filter(MetaFinanceira.user_id == current_user.id)
    
    if status:
        query = query.filter(MetaFinanceira.status == status)
    
    return query.order_by(MetaFinanceira.data_meta).all()

@router.get("/metas/{meta_id}", response_model=MetaFinanceiraResponse)
def obter_meta_financeira(
    meta_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obter meta financeira específica"""
    meta = db.query(MetaFinanceira).filter(
        MetaFinanceira.id == meta_id,
        MetaFinanceira.user_id == current_user.id
    ).first()
    
    if not meta:
        raise HTTPException(status_code=404, detail="Meta não encontrada")
    
    return meta

@router.put("/metas/{meta_id}", response_model=MetaFinanceiraResponse)
def atualizar_meta_financeira(
    meta_id: int,
    meta_update: MetaFinanceiraUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Atualizar meta financeira"""
    meta = db.query(MetaFinanceira).filter(
        MetaFinanceira.id == meta_id,
        MetaFinanceira.user_id == current_user.id
    ).first()
    
    if not meta:
        raise HTTPException(status_code=404, detail="Meta não encontrada")
    
    for field, value in meta_update.dict(exclude_unset=True).items():
        setattr(meta, field, value)
    
    db.commit()
    db.refresh(meta)
    return meta

@router.delete("/metas/{meta_id}")
def deletar_meta_financeira(
    meta_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Deletar meta financeira"""
    meta = db.query(MetaFinanceira).filter(
        MetaFinanceira.id == meta_id,
        MetaFinanceira.user_id == current_user.id
    ).first()
    
    if not meta:
        raise HTTPException(status_code=404, detail="Meta não encontrada")
    
    # Deletar transações relacionadas
    db.query(TransacaoMeta).filter(TransacaoMeta.meta_id == meta_id).delete()
    
    db.delete(meta)
    db.commit()
    return {"message": "Meta deletada com sucesso"}

# ==================== TRANSAÇÕES DE META ====================

@router.post("/metas/{meta_id}/transacoes", response_model=TransacaoMetaResponse)
def adicionar_transacao_meta(
    meta_id: int,
    transacao: TransacaoMetaCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Adicionar transação para uma meta"""
    # Verificar se a meta existe
    meta = db.query(MetaFinanceira).filter(
        MetaFinanceira.id == meta_id,
        MetaFinanceira.user_id == current_user.id
    ).first()
    
    if not meta:
        raise HTTPException(status_code=404, detail="Meta não encontrada")
    
    # Criar transação
    db_transacao = TransacaoMeta(
        user_id=current_user.id,
        meta_id=meta_id,
        **transacao.dict()
    )
    db.add(db_transacao)
    
    # Atualizar valor atual da meta
    meta.valor_atual += transacao.valor
    
    # Verificar se a meta foi concluída
    if meta.valor_atual >= meta.valor_meta:
        meta.status = StatusMeta.CONCLUIDA
    
    db.commit()
    db.refresh(db_transacao)
    return db_transacao

@router.get("/metas/{meta_id}/transacoes", response_model=List[TransacaoMetaResponse])
def listar_transacoes_meta(
    meta_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Listar transações de uma meta"""
    # Verificar se a meta existe
    meta = db.query(MetaFinanceira).filter(
        MetaFinanceira.id == meta_id,
        MetaFinanceira.user_id == current_user.id
    ).first()
    
    if not meta:
        raise HTTPException(status_code=404, detail="Meta não encontrada")
    
    transacoes = db.query(TransacaoMeta).filter(
        TransacaoMeta.meta_id == meta_id,
        TransacaoMeta.user_id == current_user.id
    ).order_by(TransacaoMeta.data_transacao.desc()).all()
    
    return transacoes

@router.delete("/transacoes/{transacao_id}")
def deletar_transacao_meta(
    transacao_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Deletar transação de meta"""
    transacao = db.query(TransacaoMeta).filter(
        TransacaoMeta.id == transacao_id,
        TransacaoMeta.user_id == current_user.id
    ).first()
    
    if not transacao:
        raise HTTPException(status_code=404, detail="Transação não encontrada")
    
    # Atualizar valor atual da meta
    meta = db.query(MetaFinanceira).filter(MetaFinanceira.id == transacao.meta_id).first()
    meta.valor_atual -= transacao.valor
    
    # Verificar se a meta ainda está concluída
    if meta.valor_atual < meta.valor_meta and meta.status == StatusMeta.CONCLUIDA:
        meta.status = StatusMeta.ATIVA
    
    db.delete(transacao)
    db.commit()
    return {"message": "Transação deletada com sucesso"}

# ==================== INVESTIMENTOS ====================

@router.post("/investimentos", response_model=InvestimentoResponse)
def criar_investimento(
    investimento: InvestimentoCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Criar novo investimento"""
    db_investimento = Investimento(
        user_id=current_user.id,
        **investimento.dict()
    )
    db.add(db_investimento)
    db.commit()
    db.refresh(db_investimento)
    return db_investimento

@router.get("/investimentos", response_model=List[InvestimentoResponse])
def listar_investimentos(
    tipo: Optional[TipoInvestimento] = None,
    ativo: Optional[bool] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Listar investimentos"""
    query = db.query(Investimento).filter(Investimento.user_id == current_user.id)
    
    if tipo:
        query = query.filter(Investimento.tipo == tipo)
    if ativo is not None:
        query = query.filter(Investimento.ativo == ativo)
    
    return query.order_by(Investimento.data_investimento.desc()).all()

@router.get("/investimentos/{investimento_id}", response_model=InvestimentoResponse)
def obter_investimento(
    investimento_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obter investimento específico"""
    investimento = db.query(Investimento).filter(
        Investimento.id == investimento_id,
        Investimento.user_id == current_user.id
    ).first()
    
    if not investimento:
        raise HTTPException(status_code=404, detail="Investimento não encontrado")
    
    return investimento

@router.put("/investimentos/{investimento_id}", response_model=InvestimentoResponse)
def atualizar_investimento(
    investimento_id: int,
    investimento_update: InvestimentoUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Atualizar investimento"""
    investimento = db.query(Investimento).filter(
        Investimento.id == investimento_id,
        Investimento.user_id == current_user.id
    ).first()
    
    if not investimento:
        raise HTTPException(status_code=404, detail="Investimento não encontrado")
    
    for field, value in investimento_update.dict(exclude_unset=True).items():
        setattr(investimento, field, value)
    
    db.commit()
    db.refresh(investimento)
    return investimento

@router.delete("/investimentos/{investimento_id}")
def deletar_investimento(
    investimento_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Deletar investimento"""
    investimento = db.query(Investimento).filter(
        Investimento.id == investimento_id,
        Investimento.user_id == current_user.id
    ).first()
    
    if not investimento:
        raise HTTPException(status_code=404, detail="Investimento não encontrado")
    
    db.delete(investimento)
    db.commit()
    return {"message": "Investimento deletado com sucesso"}

# ==================== DASHBOARD E RELATÓRIOS ====================

@router.get("/dashboard", response_model=DashboardResponse)
def obter_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obter dados do dashboard financeiro"""
    hoje = date.today()
    inicio_mes = hoje.replace(day=1)
    
    # Receitas do mês
    receitas_mes = db.query(func.sum(ContaReceber.valor)).filter(
        ContaReceber.user_id == current_user.id,
        ContaReceber.status == StatusConta.PAGO,
        func.extract('month', ContaReceber.data_recebimento) == hoje.month,
        func.extract('year', ContaReceber.data_recebimento) == hoje.year
    ).scalar() or 0
    
    # Despesas do mês
    despesas_mes = db.query(func.sum(ContaPagar.valor)).filter(
        ContaPagar.user_id == current_user.id,
        ContaPagar.status == StatusConta.PAGO,
        func.extract('month', ContaPagar.data_pagamento) == hoje.month,
        func.extract('year', ContaPagar.data_pagamento) == hoje.year
    ).scalar() or 0
    
    # Total investido
    total_investido = db.query(func.sum(Investimento.valor_atual)).filter(
        Investimento.user_id == current_user.id,
        Investimento.ativo == True
    ).scalar() or 0
    
    # Metas ativas e concluídas
    metas_ativas = db.query(func.count(MetaFinanceira.id)).filter(
        MetaFinanceira.user_id == current_user.id,
        MetaFinanceira.status == StatusMeta.ATIVA
    ).scalar() or 0
    
    metas_concluidas = db.query(func.count(MetaFinanceira.id)).filter(
        MetaFinanceira.user_id == current_user.id,
        MetaFinanceira.status == StatusMeta.CONCLUIDA
    ).scalar() or 0
    
    # Próximas contas (próximos 7 dias)
    proximas_contas = db.query(ContaPagar).filter(
        ContaPagar.user_id == current_user.id,
        ContaPagar.status == StatusConta.PENDENTE,
        ContaPagar.data_vencimento <= hoje + timedelta(days=7)
    ).order_by(ContaPagar.data_vencimento).limit(5).all()
    
    # Metas próximas (próximos 30 dias)
    metas_proximas = db.query(MetaFinanceira).filter(
        MetaFinanceira.user_id == current_user.id,
        MetaFinanceira.status == StatusMeta.ATIVA,
        MetaFinanceira.data_meta <= hoje + timedelta(days=30)
    ).order_by(MetaFinanceira.data_meta).limit(5).all()
    
    return DashboardResponse(
        saldo_atual=receitas_mes - despesas_mes,
        receitas_mes=receitas_mes,
        despesas_mes=despesas_mes,
        saldo_mes=receitas_mes - despesas_mes,
        total_investido=total_investido,
        metas_ativas=metas_ativas,
        metas_concluidas=metas_concluidas,
        proximas_contas=proximas_contas,
        metas_proximas=metas_proximas
    )

@router.get("/graficos/mensal", response_model=List[GraficoMensalResponse])
def obter_grafico_mensal(
    meses: int = Query(12, description="Número de meses para o gráfico"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obter dados para gráfico mensal"""
    hoje = date.today()
    dados = []
    
    for i in range(meses):
        data_ref = hoje - timedelta(days=30 * i)
        mes = data_ref.month
        ano = data_ref.year
        
        # Receitas do mês
        receitas = db.query(func.sum(ContaReceber.valor)).filter(
            ContaReceber.user_id == current_user.id,
            ContaReceber.status == StatusConta.PAGO,
            func.extract('month', ContaReceber.data_recebimento) == mes,
            func.extract('year', ContaReceber.data_recebimento) == ano
        ).scalar() or 0
        
        # Despesas do mês
        despesas = db.query(func.sum(ContaPagar.valor)).filter(
            ContaPagar.user_id == current_user.id,
            ContaPagar.status == StatusConta.PAGO,
            func.extract('month', ContaPagar.data_pagamento) == mes,
            func.extract('year', ContaPagar.data_pagamento) == ano
        ).scalar() or 0
        
        dados.append(GraficoMensalResponse(
            mes=f"{mes:02d}/{ano}",
            receitas=receitas,
            despesas=despesas,
            saldo=receitas - despesas
        ))
    
    return list(reversed(dados))

@router.get("/relatorios/categorias", response_model=List[RelatorioCategoriaResponse])
def obter_relatorio_categorias(
    tipo: str = Query("despesas", description="Tipo: 'despesas' ou 'receitas'"),
    mes: Optional[int] = None,
    ano: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obter relatório por categorias"""
    hoje = date.today()
    mes_ref = mes or hoje.month
    ano_ref = ano or hoje.year
    
    if tipo == "despesas":
        query = db.query(
            ContaPagar.categoria,
            func.sum(ContaPagar.valor).label('total'),
            func.count(ContaPagar.id).label('quantidade')
        ).filter(
            ContaPagar.user_id == current_user.id,
            ContaPagar.status == StatusConta.PAGO,
            func.extract('month', ContaPagar.data_pagamento) == mes_ref,
            func.extract('year', ContaPagar.data_pagamento) == ano_ref
        ).group_by(ContaPagar.categoria)
    else:
        query = db.query(
            ContaReceber.categoria,
            func.sum(ContaReceber.valor).label('total'),
            func.count(ContaReceber.id).label('quantidade')
        ).filter(
            ContaReceber.user_id == current_user.id,
            ContaReceber.status == StatusConta.PAGO,
            func.extract('month', ContaReceber.data_recebimento) == mes_ref,
            func.extract('year', ContaReceber.data_recebimento) == ano_ref
        ).group_by(ContaReceber.categoria)
    
    resultados = query.all()
    total_geral = sum(r.total for r in resultados)
    
    relatorio = []
    for resultado in resultados:
        percentual = (resultado.total / total_geral * 100) if total_geral > 0 else 0
        relatorio.append(RelatorioCategoriaResponse(
            categoria=resultado.categoria.value,
            total=resultado.total,
            percentual=round(percentual, 2),
            quantidade=resultado.quantidade
        ))
    
    return sorted(relatorio, key=lambda x: x.total, reverse=True)

