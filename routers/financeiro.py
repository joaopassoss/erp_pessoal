from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from database import get_db
from models import (
    User, ContaPagar, ContaReceber, MetaFinanceira, TransacaoMeta, 
    Investimento, ResumoFinanceiro, MetaMensal, CategoriaConta, StatusConta, 
    TipoInvestimento, StatusMeta
)
from schemas import (
    ContaPagarCreate, ContaPagarUpdate, ContaPagarResponse,
    ContaPagarParceladaCreate, AnteciparParcelaRequest,
    ContaReceberCreate, ContaReceberUpdate, ContaReceberResponse,
    MetaFinanceiraCreate, MetaFinanceiraUpdate, MetaFinanceiraResponse,
    TransacaoMetaCreate, TransacaoMetaResponse,
    InvestimentoCreate, InvestimentoUpdate, InvestimentoResponse,
    DashboardResponse, GraficoMensalResponse, RelatorioCategoriaResponse,
    RelatorioMensalResponse, FluxoCaixaMensalResponse, ComparativoMensalResponse,
    AlertasMensaisResponse, MetaMensalCreate, MetaMensalUpdate, MetaMensalResponse,
    DashboardMensalResponse
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

@router.post("/contas-pagar/parcelada", response_model=List[ContaPagarResponse])
def criar_conta_parcelada(
    conta: ContaPagarParceladaCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Criar conta parcelada com múltiplas parcelas"""
    from datetime import timedelta
    
    # Calcular valor de cada parcela
    valor_parcela = conta.valor_total / conta.total_parcelas
    
    # Criar todas as parcelas
    parcelas = []
    for i in range(conta.total_parcelas):
        # Calcular data de vencimento (incrementar mês)
        if i == 0:
            data_vencimento = conta.data_vencimento_primeira
        else:
            # Adicionar i meses à data inicial
            data_vencimento = conta.data_vencimento_primeira
            for _ in range(i):
                # Adicionar um mês
                if data_vencimento.month == 12:
                    data_vencimento = data_vencimento.replace(year=data_vencimento.year + 1, month=1)
                else:
                    data_vencimento = data_vencimento.replace(month=data_vencimento.month + 1)
        
        parcela = ContaPagar(
            user_id=current_user.id,
            descricao=f"{conta.descricao} - Parcela {i+1}/{conta.total_parcelas}",
            valor=valor_parcela,
            data_vencimento=data_vencimento,
            categoria=conta.categoria,
            observacoes=conta.observacoes,
            is_parcelada=True,
            parcela_atual=i+1,
            total_parcelas=conta.total_parcelas,
            valor_parcela=valor_parcela,
            parcela_original_id=None  # Será definido após criar a primeira parcela
        )
        db.add(parcela)
        db.flush()  # Para obter o ID da primeira parcela
        
        # Definir o ID da conta original (primeira parcela)
        if i == 0:
            parcela_original_id = parcela.id
            parcela.parcela_original_id = parcela.id
        else:
            parcela.parcela_original_id = parcela_original_id
        
        parcelas.append(parcela)
    
    db.commit()
    
    # Refresh todas as parcelas para retornar com IDs
    for parcela in parcelas:
        db.refresh(parcela)
    
    return parcelas

@router.get("/contas-pagar/{conta_id}/parcelas", response_model=List[ContaPagarResponse])
def listar_parcelas(
    conta_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Listar todas as parcelas de uma conta"""
    # Buscar a conta original
    conta_original = db.query(ContaPagar).filter(
        ContaPagar.id == conta_id,
        ContaPagar.user_id == current_user.id
    ).first()
    
    if not conta_original:
        raise HTTPException(status_code=404, detail="Conta não encontrada")
    
    # Se for uma parcela, buscar a conta original
    if conta_original.parcela_original_id and conta_original.parcela_original_id != conta_original.id:
        conta_original_id = conta_original.parcela_original_id
    else:
        conta_original_id = conta_id
    
    # Buscar todas as parcelas
    parcelas = db.query(ContaPagar).filter(
        ContaPagar.parcela_original_id == conta_original_id,
        ContaPagar.user_id == current_user.id
    ).order_by(ContaPagar.parcela_atual).all()
    
    return parcelas

@router.put("/contas-pagar/{parcela_id}/antecipar")
def antecipar_parcela(
    parcela_id: int,
    request: AnteciparParcelaRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Antecipar o pagamento de uma parcela"""
    parcela = db.query(ContaPagar).filter(
        ContaPagar.id == parcela_id,
        ContaPagar.user_id == current_user.id
    ).first()
    
    if not parcela:
        raise HTTPException(status_code=404, detail="Parcela não encontrada")
    
    if not parcela.is_parcelada:
        raise HTTPException(status_code=400, detail="Esta conta não é parcelada")
    
    # Atualizar data de vencimento
    parcela.data_vencimento = request.nova_data_vencimento
    
    db.commit()
    return {"message": "Parcela antecipada com sucesso"}

@router.post("/contas-pagar/{parcela_id}/pagar-parcela")
def pagar_parcela(
    parcela_id: int,
    data_pagamento: Optional[date] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Pagar uma parcela específica"""
    parcela = db.query(ContaPagar).filter(
        ContaPagar.id == parcela_id,
        ContaPagar.user_id == current_user.id
    ).first()
    
    if not parcela:
        raise HTTPException(status_code=404, detail="Parcela não encontrada")
    
    if not parcela.is_parcelada:
        raise HTTPException(status_code=400, detail="Esta conta não é parcelada")
    
    parcela.status = StatusConta.PAGO
    parcela.data_pagamento = data_pagamento or date.today()
    
    db.commit()
    return {"message": "Parcela paga com sucesso"}

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
    mes: Optional[int] = None,
    ano: Optional[int] = None,
    tipo: str = Query("mensal", description="Tipo: 'mensal', 'anual' ou 'total'"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obter dados do dashboard financeiro"""
    hoje = date.today()
    
    # Definir parâmetros baseados no tipo
    if tipo == "mensal":
        mes_ref = mes or hoje.month
        ano_ref = ano or hoje.year
        filtro_mes = mes_ref
        filtro_ano = ano_ref
    elif tipo == "anual":
        ano_ref = ano or hoje.year
        filtro_mes = None
        filtro_ano = ano_ref
    else:  # total
        filtro_mes = None
        filtro_ano = None
    
    # Construir filtros baseados no tipo
    filtros_receitas = [ContaReceber.user_id == current_user.id, ContaReceber.status == StatusConta.PAGO]
    filtros_despesas = [ContaPagar.user_id == current_user.id, ContaPagar.status == StatusConta.PAGO]
    
    if filtro_mes:
        # Para receitas: filtrar por data_vencimento (quando vence) - SQLite
        filtros_receitas.append(func.strftime('%m', ContaReceber.data_vencimento) == f'{filtro_mes:02d}')
        # Para despesas: filtrar por data_vencimento (quando vence) - SQLite
        filtros_despesas.append(func.strftime('%m', ContaPagar.data_vencimento) == f'{filtro_mes:02d}')
    
    if filtro_ano:
        # Para receitas: filtrar por data_vencimento (quando vence) - SQLite
        filtros_receitas.append(func.strftime('%Y', ContaReceber.data_vencimento) == str(filtro_ano))
        # Para despesas: filtrar por data_vencimento (quando vence) - SQLite
        filtros_despesas.append(func.strftime('%Y', ContaPagar.data_vencimento) == str(filtro_ano))
    
    # Receitas
    receitas_mes = db.query(func.sum(ContaReceber.valor)).filter(*filtros_receitas).scalar() or 0
    
    # Despesas
    despesas_mes = db.query(func.sum(ContaPagar.valor)).filter(*filtros_despesas).scalar() or 0
    
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

# ==================== RELATÓRIOS MENSALS ====================

@router.get("/relatorios/mensal", response_model=RelatorioMensalResponse)
def obter_relatorio_mensal(
    mes: Optional[int] = None,
    ano: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obter relatório financeiro completo do mês"""
    hoje = date.today()
    mes_ref = mes or hoje.month
    ano_ref = ano or hoje.year
    
    # Calcular totais do mês
    receitas_mes = db.query(func.sum(ContaReceber.valor)).filter(
        ContaReceber.user_id == current_user.id,
        ContaReceber.status == StatusConta.PAGO,
        func.extract('month', ContaReceber.data_recebimento) == mes_ref,
        func.extract('year', ContaReceber.data_recebimento) == ano_ref
    ).scalar() or 0
    
    despesas_mes = db.query(func.sum(ContaPagar.valor)).filter(
        ContaPagar.user_id == current_user.id,
        ContaPagar.status == StatusConta.PAGO,
        func.extract('month', ContaPagar.data_pagamento) == mes_ref,
        func.extract('year', ContaPagar.data_pagamento) == ano_ref
    ).scalar() or 0
    
    saldo_mensal = receitas_mes - despesas_mes
    
    # Total investido no mês
    total_investido = db.query(func.sum(Investimento.valor_investido)).filter(
        Investimento.user_id == current_user.id,
        func.extract('month', Investimento.data_investimento) == mes_ref,
        func.extract('year', Investimento.data_investimento) == ano_ref
    ).scalar() or 0
    
    # Total em metas no mês
    total_metas = db.query(func.sum(TransacaoMeta.valor)).filter(
        TransacaoMeta.user_id == current_user.id,
        func.extract('month', TransacaoMeta.data_transacao) == mes_ref,
        func.extract('year', TransacaoMeta.data_transacao) == ano_ref
    ).scalar() or 0
    
    # Contas pagas e vencidas
    contas_pagas = db.query(func.count(ContaPagar.id)).filter(
        ContaPagar.user_id == current_user.id,
        ContaPagar.status == StatusConta.PAGO,
        func.extract('month', ContaPagar.data_pagamento) == mes_ref,
        func.extract('year', ContaPagar.data_pagamento) == ano_ref
    ).scalar() or 0
    
    contas_vencidas = db.query(func.count(ContaPagar.id)).filter(
        ContaPagar.user_id == current_user.id,
        ContaPagar.status == StatusConta.VENCIDO,
        func.extract('month', ContaPagar.data_vencimento) == mes_ref,
        func.extract('year', ContaPagar.data_vencimento) == ano_ref
    ).scalar() or 0
    
    # Metas concluídas e ativas
    metas_concluidas = db.query(func.count(MetaFinanceira.id)).filter(
        MetaFinanceira.user_id == current_user.id,
        MetaFinanceira.status == StatusMeta.CONCLUIDA,
        func.extract('month', MetaFinanceira.updated_at) == mes_ref,
        func.extract('year', MetaFinanceira.updated_at) == ano_ref
    ).scalar() or 0
    
    metas_ativas = db.query(func.count(MetaFinanceira.id)).filter(
        MetaFinanceira.user_id == current_user.id,
        MetaFinanceira.status == StatusMeta.ATIVA
    ).scalar() or 0
    
    # Relatórios por categoria
    receitas_por_categoria = obter_relatorio_categorias("receitas", mes_ref, ano_ref, current_user, db)
    despesas_por_categoria = obter_relatorio_categorias("despesas", mes_ref, ano_ref, current_user, db)
    
    return RelatorioMensalResponse(
        mes=mes_ref,
        ano=ano_ref,
        total_receitas=receitas_mes,
        total_despesas=despesas_mes,
        saldo_mensal=saldo_mensal,
        total_investido=total_investido,
        total_metas=total_metas,
        receitas_por_categoria=receitas_por_categoria,
        despesas_por_categoria=despesas_por_categoria,
        contas_pagas=contas_pagas,
        contas_vencidas=contas_vencidas,
        metas_concluidas=metas_concluidas,
        metas_ativas=metas_ativas
    )

@router.get("/relatorios/fluxo-caixa-mensal", response_model=FluxoCaixaMensalResponse)
def obter_fluxo_caixa_mensal(
    mes: Optional[int] = None,
    ano: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obter fluxo de caixa mensal detalhado"""
    hoje = date.today()
    mes_ref = mes or hoje.month
    ano_ref = ano or hoje.year
    
    # Saldo inicial (soma de todos os saldos até o mês anterior)
    saldo_inicial = 0
    if mes_ref > 1:
        # Calcular saldo acumulado até o mês anterior
        for m in range(1, mes_ref):
            receitas_ant = db.query(func.sum(ContaReceber.valor)).filter(
                ContaReceber.user_id == current_user.id,
                ContaReceber.status == StatusConta.PAGO,
                func.extract('month', ContaReceber.data_recebimento) == m,
                func.extract('year', ContaReceber.data_recebimento) == ano_ref
            ).scalar() or 0
            
            despesas_ant = db.query(func.sum(ContaPagar.valor)).filter(
                ContaPagar.user_id == current_user.id,
                ContaPagar.status == StatusConta.PAGO,
                func.extract('month', ContaPagar.data_pagamento) == m,
                func.extract('year', ContaPagar.data_pagamento) == ano_ref
            ).scalar() or 0
            
            saldo_inicial += (receitas_ant - despesas_ant)
    
    # Entradas do mês
    entradas = db.query(func.sum(ContaReceber.valor)).filter(
        ContaReceber.user_id == current_user.id,
        ContaReceber.status == StatusConta.PAGO,
        func.extract('month', ContaReceber.data_recebimento) == mes_ref,
        func.extract('year', ContaReceber.data_recebimento) == ano_ref
    ).scalar() or 0
    
    # Saídas do mês
    saidas = db.query(func.sum(ContaPagar.valor)).filter(
        ContaPagar.user_id == current_user.id,
        ContaPagar.status == StatusConta.PAGO,
        func.extract('month', ContaPagar.data_pagamento) == mes_ref,
        func.extract('year', ContaPagar.data_pagamento) == ano_ref
    ).scalar() or 0
    
    saldo_final = saldo_inicial + entradas - saidas
    variacao_mensal = entradas - saidas
    percentual_variacao = (variacao_mensal / saldo_inicial * 100) if saldo_inicial > 0 else 0
    
    return FluxoCaixaMensalResponse(
        mes=mes_ref,
        ano=ano_ref,
        saldo_inicial=saldo_inicial,
        entradas=entradas,
        saidas=saidas,
        saldo_final=saldo_final,
        variacao_mensal=variacao_mensal,
        percentual_variacao=round(percentual_variacao, 2)
    )

@router.get("/relatorios/comparativo-mensal", response_model=ComparativoMensalResponse)
def obter_comparativo_mensal(
    mes: Optional[int] = None,
    ano: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Comparar mês atual com mês anterior"""
    hoje = date.today()
    mes_atual = mes or hoje.month
    ano_atual = ano or hoje.year
    
    # Calcular mês anterior
    if mes_atual == 1:
        mes_anterior = 12
        ano_anterior = ano_atual - 1
    else:
        mes_anterior = mes_atual - 1
        ano_anterior = ano_atual
    
    # Obter relatórios
    relatorio_atual = obter_relatorio_mensal(mes_atual, ano_atual, current_user, db)
    relatorio_anterior = obter_relatorio_mensal(mes_anterior, ano_anterior, current_user, db)
    
    # Calcular variações
    variacao_receitas = relatorio_atual.total_receitas - relatorio_anterior.total_receitas
    variacao_despesas = relatorio_atual.total_despesas - relatorio_anterior.total_despesas
    variacao_saldo = relatorio_atual.saldo_mensal - relatorio_anterior.saldo_mensal
    
    # Determinar tendência
    if variacao_saldo > 0:
        tendencia = "crescimento"
    elif variacao_saldo < 0:
        tendencia = "declinio"
    else:
        tendencia = "estavel"
    
    return ComparativoMensalResponse(
        mes_atual=relatorio_atual,
        mes_anterior=relatorio_anterior,
        variacao_receitas=variacao_receitas,
        variacao_despesas=variacao_despesas,
        variacao_saldo=variacao_saldo,
        tendencia=tendencia
    )

@router.get("/relatorios/alertas-mensais", response_model=AlertasMensaisResponse)
def obter_alertas_mensais(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obter alertas e notificações financeiras"""
    hoje = date.today()
    
    # Contas vencidas
    contas_vencidas = db.query(ContaPagar).filter(
        ContaPagar.user_id == current_user.id,
        ContaPagar.status == StatusConta.VENCIDO,
        ContaPagar.data_vencimento < hoje
    ).all()
    
    # Metas atrasadas (que passaram da data limite)
    metas_atrasadas = db.query(MetaFinanceira).filter(
        MetaFinanceira.user_id == current_user.id,
        MetaFinanceira.status == StatusMeta.ATIVA,
        MetaFinanceira.data_meta < hoje
    ).all()
    
    # Investimentos com rentabilidade negativa
    investimentos_negativos = db.query(Investimento).filter(
        Investimento.user_id == current_user.id,
        Investimento.ativo == True,
        Investimento.valor_atual < Investimento.valor_investido
    ).all()
    
    # Verificar saldo negativo
    saldo_negativo = False
    alertas_criticos = []
    
    # Calcular saldo atual
    receitas_totais = db.query(func.sum(ContaReceber.valor)).filter(
        ContaReceber.user_id == current_user.id,
        ContaReceber.status == StatusConta.PAGO
    ).scalar() or 0
    
    despesas_totais = db.query(func.sum(ContaPagar.valor)).filter(
        ContaPagar.user_id == current_user.id,
        ContaPagar.status == StatusConta.PAGO
    ).scalar() or 0
    
    saldo_atual = receitas_totais - despesas_totais
    
    if saldo_atual < 0:
        saldo_negativo = True
        alertas_criticos.append("Saldo negativo detectado!")
    
    if len(contas_vencidas) > 5:
        alertas_criticos.append("Muitas contas vencidas!")
    
    if len(metas_atrasadas) > 3:
        alertas_criticos.append("Muitas metas atrasadas!")
    
    return AlertasMensaisResponse(
        contas_vencidas=contas_vencidas,
        metas_atrasadas=metas_atrasadas,
        investimentos_negativos=investimentos_negativos,
        saldo_negativo=saldo_negativo,
        alertas_criticos=alertas_criticos
    )

@router.post("/relatorios/gerar-resumo-mensal")
def gerar_resumo_mensal_automatico(
    mes: Optional[int] = None,
    ano: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Gerar e salvar resumo financeiro mensal automaticamente"""
    hoje = date.today()
    mes_ref = mes or hoje.month
    ano_ref = ano or hoje.year
    
    # Verificar se já existe resumo para o mês
    resumo_existente = db.query(ResumoFinanceiro).filter(
        ResumoFinanceiro.user_id == current_user.id,
        ResumoFinanceiro.mes == mes_ref,
        ResumoFinanceiro.ano == ano_ref
    ).first()
    
    if resumo_existente:
        # Atualizar resumo existente
        resumo = resumo_existente
    else:
        # Criar novo resumo
        resumo = ResumoFinanceiro(
            user_id=current_user.id,
            mes=mes_ref,
            ano=ano_ref
        )
        db.add(resumo)
    
    # Calcular totais
    receitas_mes = db.query(func.sum(ContaReceber.valor)).filter(
        ContaReceber.user_id == current_user.id,
        ContaReceber.status == StatusConta.PAGO,
        func.extract('month', ContaReceber.data_recebimento) == mes_ref,
        func.extract('year', ContaReceber.data_recebimento) == ano_ref
    ).scalar() or 0
    
    despesas_mes = db.query(func.sum(ContaPagar.valor)).filter(
        ContaPagar.user_id == current_user.id,
        ContaPagar.status == StatusConta.PAGO,
        func.extract('month', ContaPagar.data_pagamento) == mes_ref,
        func.extract('year', ContaPagar.data_pagamento) == ano_ref
    ).scalar() or 0
    
    total_investido = db.query(func.sum(Investimento.valor_investido)).filter(
        Investimento.user_id == current_user.id,
        func.extract('month', Investimento.data_investimento) == mes_ref,
        func.extract('year', Investimento.data_investimento) == ano_ref
    ).scalar() or 0
    
    total_metas = db.query(func.sum(TransacaoMeta.valor)).filter(
        TransacaoMeta.user_id == current_user.id,
        func.extract('month', TransacaoMeta.data_transacao) == mes_ref,
        func.extract('year', TransacaoMeta.data_transacao) == ano_ref
    ).scalar() or 0
    
    # Atualizar resumo
    resumo.total_receitas = receitas_mes
    resumo.total_despesas = despesas_mes
    resumo.saldo_mensal = receitas_mes - despesas_mes
    resumo.total_investido = total_investido
    resumo.total_metas = total_metas
    
    db.commit()
    
    return {"message": f"Resumo mensal gerado com sucesso para {mes_ref}/{ano_ref}"}

# ==================== METAS MENSALS ====================

@router.post("/metas-mensais", response_model=MetaMensalResponse)
def criar_meta_mensal(
    meta: MetaMensalCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Criar meta mensal"""
    # Verificar se já existe meta para o mês/ano
    meta_existente = db.query(MetaMensal).filter(
        MetaMensal.user_id == current_user.id,
        MetaMensal.mes == meta.mes,
        MetaMensal.ano == meta.ano
    ).first()
    
    if meta_existente:
        raise HTTPException(status_code=400, detail="Já existe meta para este mês/ano")
    
    db_meta = MetaMensal(
        user_id=current_user.id,
        **meta.dict()
    )
    db.add(db_meta)
    db.commit()
    db.refresh(db_meta)
    
    # Atualizar valores realizados
    atualizar_meta_mensal(db_meta.id, current_user, db)
    
    return db_meta

@router.get("/metas-mensais", response_model=List[MetaMensalResponse])
def listar_metas_mensais(
    mes: Optional[int] = None,
    ano: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Listar metas mensais"""
    query = db.query(MetaMensal).filter(MetaMensal.user_id == current_user.id)
    
    if mes:
        query = query.filter(MetaMensal.mes == mes)
    if ano:
        query = query.filter(MetaMensal.ano == ano)
    
    metas = query.order_by(MetaMensal.ano.desc(), MetaMensal.mes.desc()).all()
    
    # Atualizar valores realizados para cada meta
    for meta in metas:
        atualizar_meta_mensal(meta.id, current_user, db)
    
    return metas

@router.get("/metas-mensais/{meta_id}", response_model=MetaMensalResponse)
def obter_meta_mensal(
    meta_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obter meta mensal específica"""
    meta = db.query(MetaMensal).filter(
        MetaMensal.id == meta_id,
        MetaMensal.user_id == current_user.id
    ).first()
    
    if not meta:
        raise HTTPException(status_code=404, detail="Meta mensal não encontrada")
    
    # Atualizar valores realizados
    atualizar_meta_mensal(meta.id, current_user, db)
    
    return meta

@router.put("/metas-mensais/{meta_id}", response_model=MetaMensalResponse)
def atualizar_meta_mensal_endpoint(
    meta_id: int,
    meta_update: MetaMensalUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Atualizar meta mensal"""
    meta = db.query(MetaMensal).filter(
        MetaMensal.id == meta_id,
        MetaMensal.user_id == current_user.id
    ).first()
    
    if not meta:
        raise HTTPException(status_code=404, detail="Meta mensal não encontrada")
    
    for field, value in meta_update.dict(exclude_unset=True).items():
        setattr(meta, field, value)
    
    db.commit()
    db.refresh(meta)
    
    # Atualizar valores realizados
    atualizar_meta_mensal(meta.id, current_user, db)
    
    return meta

@router.delete("/metas-mensais/{meta_id}")
def deletar_meta_mensal(
    meta_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Deletar meta mensal"""
    meta = db.query(MetaMensal).filter(
        MetaMensal.id == meta_id,
        MetaMensal.user_id == current_user.id
    ).first()
    
    if not meta:
        raise HTTPException(status_code=404, detail="Meta mensal não encontrada")
    
    db.delete(meta)
    db.commit()
    return {"message": "Meta mensal deletada com sucesso"}

@router.get("/dashboard-mensal", response_model=DashboardMensalResponse)
def obter_dashboard_mensal(
    mes: Optional[int] = None,
    ano: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obter dashboard mensal completo"""
    hoje = date.today()
    mes_ref = mes or hoje.month
    ano_ref = ano or hoje.year
    
    # Obter todos os dados do mês
    resumo_mensal = obter_relatorio_mensal(mes_ref, ano_ref, current_user, db)
    fluxo_caixa = obter_fluxo_caixa_mensal(mes_ref, ano_ref, current_user, db)
    comparativo = obter_comparativo_mensal(mes_ref, ano_ref, current_user, db)
    alertas = obter_alertas_mensais(current_user, db)
    
    # Buscar meta mensal
    meta_mensal = db.query(MetaMensal).filter(
        MetaMensal.user_id == current_user.id,
        MetaMensal.mes == mes_ref,
        MetaMensal.ano == ano_ref
    ).first()
    
    if meta_mensal:
        atualizar_meta_mensal(meta_mensal.id, current_user, db)
    
    # Próximos vencimentos (próximos 7 dias)
    data_limite = hoje + timedelta(days=7)
    proximos_vencimentos = db.query(ContaPagar).filter(
        ContaPagar.user_id == current_user.id,
        ContaPagar.status == StatusConta.PENDENTE,
        ContaPagar.data_vencimento <= data_limite,
        ContaPagar.data_vencimento >= hoje
    ).order_by(ContaPagar.data_vencimento).limit(10).all()
    
    # Metas próximas (próximos 30 dias)
    data_limite_metas = hoje + timedelta(days=30)
    metas_proximas = db.query(MetaFinanceira).filter(
        MetaFinanceira.user_id == current_user.id,
        MetaFinanceira.status == StatusMeta.ATIVA,
        MetaFinanceira.data_meta <= data_limite_metas,
        MetaFinanceira.data_meta >= hoje
    ).order_by(MetaFinanceira.data_meta).limit(5).all()
    
    return DashboardMensalResponse(
        mes=mes_ref,
        ano=ano_ref,
        resumo_mensal=resumo_mensal,
        fluxo_caixa=fluxo_caixa,
        comparativo=comparativo,
        alertas=alertas,
        metas_mensais=meta_mensal,
        proximos_vencimentos=proximos_vencimentos,
        metas_proximas=metas_proximas
    )

def atualizar_meta_mensal(meta_id: int, current_user: User, db: Session):
    """Função auxiliar para atualizar valores realizados de uma meta mensal"""
    meta = db.query(MetaMensal).filter(
        MetaMensal.id == meta_id,
        MetaMensal.user_id == current_user.id
    ).first()
    
    if not meta:
        return
    
    # Calcular valores realizados
    receita_realizada = db.query(func.sum(ContaReceber.valor)).filter(
        ContaReceber.user_id == current_user.id,
        ContaReceber.status == StatusConta.PAGO,
        func.extract('month', ContaReceber.data_recebimento) == meta.mes,
        func.extract('year', ContaReceber.data_recebimento) == meta.ano
    ).scalar() or 0
    
    despesa_realizada = db.query(func.sum(ContaPagar.valor)).filter(
        ContaPagar.user_id == current_user.id,
        ContaPagar.status == StatusConta.PAGO,
        func.extract('month', ContaPagar.data_pagamento) == meta.mes,
        func.extract('year', ContaPagar.data_pagamento) == meta.ano
    ).scalar() or 0
    
    investimento_realizado = db.query(func.sum(Investimento.valor_investido)).filter(
        Investimento.user_id == current_user.id,
        func.extract('month', Investimento.data_investimento) == meta.mes,
        func.extract('year', Investimento.data_investimento) == meta.ano
    ).scalar() or 0
    
    poupanca_realizada = db.query(func.sum(TransacaoMeta.valor)).filter(
        TransacaoMeta.user_id == current_user.id,
        func.extract('month', TransacaoMeta.data_transacao) == meta.mes,
        func.extract('year', TransacaoMeta.data_transacao) == meta.ano
    ).scalar() or 0
    
    # Calcular percentuais
    percentual_receita = (receita_realizada / meta.meta_receita * 100) if meta.meta_receita > 0 else 0
    percentual_despesa = (despesa_realizada / meta.meta_despesa * 100) if meta.meta_despesa > 0 else 0
    percentual_investimento = (investimento_realizado / meta.meta_investimento * 100) if meta.meta_investimento > 0 else 0
    percentual_poupanca = (poupanca_realizada / meta.meta_poupanca * 100) if meta.meta_poupanca > 0 else 0
    
    # Determinar status geral
    percentual_medio = (percentual_receita + percentual_despesa + percentual_investimento + percentual_poupanca) / 4
    
    if percentual_medio >= 100:
        status_geral = "excelente"
    elif percentual_medio >= 80:
        status_geral = "bom"
    elif percentual_medio >= 60:
        status_geral = "regular"
    else:
        status_geral = "ruim"
    
    # Atualizar meta
    meta.receita_realizada = receita_realizada
    meta.despesa_realizada = despesa_realizada
    meta.investimento_realizado = investimento_realizado
    meta.poupanca_realizada = poupanca_realizada
    meta.percentual_receita = round(percentual_receita, 2)
    meta.percentual_despesa = round(percentual_despesa, 2)
    meta.percentual_investimento = round(percentual_investimento, 2)
    meta.percentual_poupanca = round(percentual_poupanca, 2)
    meta.status_geral = status_geral
    
    db.commit()

# ==================== EXPORTAÇÃO DE RELATÓRIOS ====================

@router.get("/relatorios/exportar-mensal")
def exportar_relatorio_mensal(
    mes: Optional[int] = None,
    ano: Optional[int] = None,
    formato: str = Query("json", description="Formato: 'json' ou 'csv'"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Exportar relatório mensal em JSON ou CSV"""
    hoje = date.today()
    mes_ref = mes or hoje.month
    ano_ref = ano or hoje.year
    
    # Obter dados do relatório
    relatorio = obter_relatorio_mensal(mes_ref, ano_ref, current_user, db)
    fluxo_caixa = obter_fluxo_caixa_mensal(mes_ref, ano_ref, current_user, db)
    comparativo = obter_comparativo_mensal(mes_ref, ano_ref, current_user, db)
    alertas = obter_alertas_mensais(current_user, db)
    
    # Buscar meta mensal
    meta_mensal = db.query(MetaMensal).filter(
        MetaMensal.user_id == current_user.id,
        MetaMensal.mes == mes_ref,
        MetaMensal.ano == ano_ref
    ).first()
    
    if meta_mensal:
        atualizar_meta_mensal(meta_mensal.id, current_user, db)
    
    # Montar dados para exportação
    dados_exportacao = {
        "usuario": current_user.full_name,
        "mes": mes_ref,
        "ano": ano_ref,
        "data_exportacao": datetime.now().isoformat(),
        "resumo_mensal": {
            "total_receitas": relatorio.total_receitas,
            "total_despesas": relatorio.total_despesas,
            "saldo_mensal": relatorio.saldo_mensal,
            "total_investido": relatorio.total_investido,
            "total_metas": relatorio.total_metas,
            "contas_pagas": relatorio.contas_pagas,
            "contas_vencidas": relatorio.contas_vencidas,
            "metas_concluidas": relatorio.metas_concluidas,
            "metas_ativas": relatorio.metas_ativas
        },
        "fluxo_caixa": {
            "saldo_inicial": fluxo_caixa.saldo_inicial,
            "entradas": fluxo_caixa.entradas,
            "saidas": fluxo_caixa.saidas,
            "saldo_final": fluxo_caixa.saldo_final,
            "variacao_mensal": fluxo_caixa.variacao_mensal,
            "percentual_variacao": fluxo_caixa.percentual_variacao
        },
        "comparativo": {
            "variacao_receitas": comparativo.variacao_receitas,
            "variacao_despesas": comparativo.variacao_despesas,
            "variacao_saldo": comparativo.variacao_saldo,
            "tendencia": comparativo.tendencia
        },
        "alertas": {
            "saldo_negativo": alertas.saldo_negativo,
            "contas_vencidas_count": len(alertas.contas_vencidas),
            "metas_atrasadas_count": len(alertas.metas_atrasadas),
            "investimentos_negativos_count": len(alertas.investimentos_negativos),
            "alertas_criticos": alertas.alertas_criticos
        },
        "receitas_por_categoria": [
            {
                "categoria": item.categoria,
                "total": item.total,
                "percentual": item.percentual,
                "quantidade": item.quantidade
            } for item in relatorio.receitas_por_categoria
        ],
        "despesas_por_categoria": [
            {
                "categoria": item.categoria,
                "total": item.total,
                "percentual": item.percentual,
                "quantidade": item.quantidade
            } for item in relatorio.despesas_por_categoria
        ]
    }
    
    if meta_mensal:
        dados_exportacao["meta_mensal"] = {
            "meta_receita": meta_mensal.meta_receita,
            "meta_despesa": meta_mensal.meta_despesa,
            "meta_investimento": meta_mensal.meta_investimento,
            "meta_poupanca": meta_mensal.meta_poupanca,
            "receita_realizada": meta_mensal.receita_realizada,
            "despesa_realizada": meta_mensal.despesa_realizada,
            "investimento_realizado": meta_mensal.investimento_realizado,
            "poupanca_realizada": meta_mensal.poupanca_realizada,
            "percentual_receita": meta_mensal.percentual_receita,
            "percentual_despesa": meta_mensal.percentual_despesa,
            "percentual_investimento": meta_mensal.percentual_investimento,
            "percentual_poupanca": meta_mensal.percentual_poupanca,
            "status_geral": meta_mensal.status_geral
        }
    
    if formato == "csv":
        # Gerar CSV
        import csv
        import io
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Cabeçalho
        writer.writerow(["Relatório Financeiro Mensal"])
        writer.writerow([f"Usuário: {current_user.full_name}"])
        writer.writerow([f"Mês/Ano: {mes_ref}/{ano_ref}"])
        writer.writerow([f"Data Exportação: {datetime.now().strftime('%d/%m/%Y %H:%M')}"])
        writer.writerow([])
        
        # Resumo
        writer.writerow(["RESUMO MENSAL"])
        writer.writerow(["Total Receitas", f"R$ {relatorio.total_receitas:.2f}"])
        writer.writerow(["Total Despesas", f"R$ {relatorio.total_despesas:.2f}"])
        writer.writerow(["Saldo Mensal", f"R$ {relatorio.saldo_mensal:.2f}"])
        writer.writerow(["Total Investido", f"R$ {relatorio.total_investido:.2f}"])
        writer.writerow(["Total Metas", f"R$ {relatorio.total_metas:.2f}"])
        writer.writerow([])
        
        # Fluxo de Caixa
        writer.writerow(["FLUXO DE CAIXA"])
        writer.writerow(["Saldo Inicial", f"R$ {fluxo_caixa.saldo_inicial:.2f}"])
        writer.writerow(["Entradas", f"R$ {fluxo_caixa.entradas:.2f}"])
        writer.writerow(["Saídas", f"R$ {fluxo_caixa.saidas:.2f}"])
        writer.writerow(["Saldo Final", f"R$ {fluxo_caixa.saldo_final:.2f}"])
        writer.writerow(["Variação Mensal", f"R$ {fluxo_caixa.variacao_mensal:.2f}"])
        writer.writerow(["% Variação", f"{fluxo_caixa.percentual_variacao:.2f}%"])
        writer.writerow([])
        
        # Receitas por Categoria
        writer.writerow(["RECEITAS POR CATEGORIA"])
        writer.writerow(["Categoria", "Total", "Percentual", "Quantidade"])
        for item in relatorio.receitas_por_categoria:
            writer.writerow([item.categoria, f"R$ {item.total:.2f}", f"{item.percentual:.2f}%", item.quantidade])
        writer.writerow([])
        
        # Despesas por Categoria
        writer.writerow(["DESPESAS POR CATEGORIA"])
        writer.writerow(["Categoria", "Total", "Percentual", "Quantidade"])
        for item in relatorio.despesas_por_categoria:
            writer.writerow([item.categoria, f"R$ {item.total:.2f}", f"{item.percentual:.2f}%", item.quantidade])
        
        csv_content = output.getvalue()
        output.close()
        
        from fastapi.responses import Response
        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=relatorio_mensal_{mes_ref}_{ano_ref}.csv"}
        )
    
    else:  # JSON
        from fastapi.responses import JSONResponse
        return JSONResponse(
            content=dados_exportacao,
            headers={"Content-Disposition": f"attachment; filename=relatorio_mensal_{mes_ref}_{ano_ref}.json"}
        )

@router.post("/relatorios/gerar-todos-meses")
def gerar_relatorios_todos_meses(
    ano: int = Query(..., description="Ano para gerar relatórios"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Gerar relatórios para todos os meses de um ano"""
    meses_gerados = []
    
    for mes in range(1, 13):
        try:
            # Gerar resumo mensal
            gerar_resumo_mensal_automatico(mes, ano, current_user, db)
            
            # Criar meta mensal se não existir
            meta_existente = db.query(MetaMensal).filter(
                MetaMensal.user_id == current_user.id,
                MetaMensal.mes == mes,
                MetaMensal.ano == ano
            ).first()
            
            if not meta_existente:
                # Criar meta mensal padrão
                meta_mensal = MetaMensal(
                    user_id=current_user.id,
                    mes=mes,
                    ano=ano,
                    meta_receita=0.0,
                    meta_despesa=0.0,
                    meta_investimento=0.0,
                    meta_poupanca=0.0,
                    observacoes=f"Meta mensal gerada automaticamente para {mes}/{ano}"
                )
                db.add(meta_mensal)
                db.commit()
            
            meses_gerados.append(f"{mes:02d}/{ano}")
            
        except Exception as e:
            print(f"Erro ao gerar relatório para {mes}/{ano}: {e}")
            continue
    
    return {
        "message": f"Relatórios gerados para {len(meses_gerados)} meses",
        "meses_gerados": meses_gerados,
        "total_meses": len(meses_gerados)
    }
