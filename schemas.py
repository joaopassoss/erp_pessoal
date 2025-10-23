from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime, date
from models import CategoriaConta, StatusConta, TipoInvestimento, StatusMeta

# Schemas para autenticação
class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# Schemas para usuário
class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: str
    phone: Optional[str] = None
    address: Optional[str] = None
    bio: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    bio: Optional[str] = None

class UserResponse(UserBase):
    id: int
    role: str
    is_active: bool
    profile_picture: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class UserRoleUpdate(BaseModel):
    role: str

class UserStatusUpdate(BaseModel):
    is_active: bool

class UserPasswordUpdate(BaseModel):
    password: str

# Schemas para Contas a Pagar
class ContaPagarBase(BaseModel):
    descricao: str
    valor: float
    data_vencimento: date
    categoria: CategoriaConta
    observacoes: Optional[str] = None

class ContaPagarCreate(ContaPagarBase):
    # Campos para parcelamento
    is_parcelada: Optional[bool] = False
    total_parcelas: Optional[int] = None
    valor_parcela: Optional[float] = None

class ContaPagarUpdate(BaseModel):
    descricao: Optional[str] = None
    valor: Optional[float] = None
    data_vencimento: Optional[date] = None
    data_pagamento: Optional[date] = None
    categoria: Optional[CategoriaConta] = None
    status: Optional[StatusConta] = None
    observacoes: Optional[str] = None

class ContaPagarResponse(ContaPagarBase):
    id: int
    user_id: int
    data_pagamento: Optional[date] = None
    status: StatusConta
    # Campos de parcelamento
    is_parcelada: bool
    parcela_atual: Optional[int] = None
    total_parcelas: Optional[int] = None
    valor_parcela: Optional[float] = None
    parcela_original_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Schema para criar conta parcelada
class ContaPagarParceladaCreate(BaseModel):
    descricao: str
    valor_total: float
    data_vencimento_primeira: date
    categoria: CategoriaConta
    total_parcelas: int
    observacoes: Optional[str] = None

# Schema para antecipar parcela
class AnteciparParcelaRequest(BaseModel):
    parcela_id: int
    nova_data_vencimento: date

# Schemas para Contas a Receber
class ContaReceberBase(BaseModel):
    descricao: str
    valor: float
    data_vencimento: date
    categoria: CategoriaConta
    observacoes: Optional[str] = None

class ContaReceberCreate(ContaReceberBase):
    pass

class ContaReceberUpdate(BaseModel):
    descricao: Optional[str] = None
    valor: Optional[float] = None
    data_vencimento: Optional[date] = None
    data_recebimento: Optional[date] = None
    categoria: Optional[CategoriaConta] = None
    status: Optional[StatusConta] = None
    observacoes: Optional[str] = None

class ContaReceberResponse(ContaReceberBase):
    id: int
    user_id: int
    data_recebimento: Optional[date] = None
    status: StatusConta
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Schemas para Metas Financeiras
class MetaFinanceiraBase(BaseModel):
    titulo: str
    descricao: Optional[str] = None
    valor_meta: float
    data_inicio: date
    data_meta: date
    cor: Optional[str] = "#3B82F6"

class MetaFinanceiraCreate(MetaFinanceiraBase):
    pass

class MetaFinanceiraUpdate(BaseModel):
    titulo: Optional[str] = None
    descricao: Optional[str] = None
    valor_meta: Optional[float] = None
    data_inicio: Optional[date] = None
    data_meta: Optional[date] = None
    status: Optional[StatusMeta] = None
    cor: Optional[str] = None

class MetaFinanceiraResponse(MetaFinanceiraBase):
    id: int
    user_id: int
    valor_atual: float
    status: StatusMeta
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Schemas para Transações de Meta
class TransacaoMetaBase(BaseModel):
    meta_id: int
    valor: float
    descricao: Optional[str] = None
    data_transacao: date

class TransacaoMetaCreate(TransacaoMetaBase):
    pass

class TransacaoMetaResponse(TransacaoMetaBase):
    id: int
    user_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Schemas para Investimentos
class InvestimentoBase(BaseModel):
    nome: str
    tipo: TipoInvestimento
    valor_investido: float
    valor_atual: float
    data_investimento: date
    data_resgate: Optional[date] = None
    rentabilidade_anual: Optional[float] = None
    observacoes: Optional[str] = None

class InvestimentoCreate(InvestimentoBase):
    pass

class InvestimentoUpdate(BaseModel):
    nome: Optional[str] = None
    tipo: Optional[TipoInvestimento] = None
    valor_investido: Optional[float] = None
    valor_atual: Optional[float] = None
    data_investimento: Optional[date] = None
    data_resgate: Optional[date] = None
    rentabilidade_anual: Optional[float] = None
    observacoes: Optional[str] = None
    ativo: Optional[bool] = None

class InvestimentoResponse(InvestimentoBase):
    id: int
    user_id: int
    ativo: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Schemas para Resumos Financeiros
class ResumoFinanceiroResponse(BaseModel):
    id: int
    user_id: int
    mes: int
    ano: int
    total_receitas: float
    total_despesas: float
    saldo_mensal: float
    total_investido: float
    total_metas: float
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Schemas para Dashboard e Relatórios
class DashboardResponse(BaseModel):
    saldo_atual: float
    receitas_mes: float
    despesas_mes: float
    saldo_mes: float
    total_investido: float
    metas_ativas: int
    metas_concluidas: int
    proximas_contas: List[ContaPagarResponse]
    metas_proximas: List[MetaFinanceiraResponse]

class GraficoMensalResponse(BaseModel):
    mes: str
    receitas: float
    despesas: float
    saldo: float

class RelatorioCategoriaResponse(BaseModel):
    categoria: str
    total: float
    percentual: float
    quantidade: int
