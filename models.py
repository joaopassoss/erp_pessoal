from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Float, ForeignKey, Date, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base
from config import ROLES
import enum

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    role = Column(String, default=ROLES["membro"])
    is_active = Column(Boolean, default=True)
    profile_picture = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    address = Column(Text, nullable=True)
    bio = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relacionamentos financeiros
    contas_pagar = relationship("ContaPagar", back_populates="user")
    contas_receber = relationship("ContaReceber", back_populates="user")
    metas_financeiras = relationship("MetaFinanceira", back_populates="user")
    investimentos = relationship("Investimento", back_populates="user")
    transacoes_meta = relationship("TransacaoMeta", back_populates="user")
    
    def is_admin(self):
        return self.role == ROLES["admin"]
    
    def is_member(self):
        return self.role == ROLES["membro"]

# Enums para categorias e status
class CategoriaConta(enum.Enum):
    ALIMENTACAO = "alimentacao"
    TRANSPORTE = "transporte"
    MORADIA = "moradia"
    SAUDE = "saude"
    EDUCACAO = "educacao"
    LAZER = "lazer"
    OUTROS = "outros"

class StatusConta(enum.Enum):
    PENDENTE = "pendente"
    PAGO = "pago"
    VENCIDO = "vencido"
    CANCELADO = "cancelado"

class TipoInvestimento(enum.Enum):
    POUPANCA = "poupanca"
    CDB = "cdb"
    LCI = "lci"
    LCA = "lca"
    FUNDOS = "fundos"
    ACOES = "acoes"
    CRIPTO = "cripto"
    OUTROS = "outros"

class StatusMeta(enum.Enum):
    ATIVA = "ativa"
    CONCLUIDA = "concluida"
    PAUSADA = "pausada"
    CANCELADA = "cancelada"

# Modelo para Contas a Pagar
class ContaPagar(Base):
    __tablename__ = "contas_pagar"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    descricao = Column(String, nullable=False)
    valor = Column(Float, nullable=False)
    data_vencimento = Column(Date, nullable=False)
    data_pagamento = Column(Date, nullable=True)
    categoria = Column(Enum(CategoriaConta), nullable=False)
    status = Column(Enum(StatusConta), default=StatusConta.PENDENTE)
    observacoes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    user = relationship("User", back_populates="contas_pagar")

# Modelo para Contas a Receber
class ContaReceber(Base):
    __tablename__ = "contas_receber"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    descricao = Column(String, nullable=False)
    valor = Column(Float, nullable=False)
    data_vencimento = Column(Date, nullable=False)
    data_recebimento = Column(Date, nullable=True)
    categoria = Column(Enum(CategoriaConta), nullable=False)
    status = Column(Enum(StatusConta), default=StatusConta.PENDENTE)
    observacoes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    user = relationship("User", back_populates="contas_receber")

# Modelo para Metas Financeiras
class MetaFinanceira(Base):
    __tablename__ = "metas_financeiras"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    titulo = Column(String, nullable=False)
    descricao = Column(Text, nullable=True)
    valor_meta = Column(Float, nullable=False)
    valor_atual = Column(Float, default=0.0)
    data_inicio = Column(Date, nullable=False)
    data_meta = Column(Date, nullable=False)
    status = Column(Enum(StatusMeta), default=StatusMeta.ATIVA)
    cor = Column(String, default="#3B82F6")  # Cor para identificação visual
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    user = relationship("User", back_populates="metas_financeiras")
    transacoes = relationship("TransacaoMeta", back_populates="meta")

# Modelo para Histórico de Transações das Metas
class TransacaoMeta(Base):
    __tablename__ = "transacoes_meta"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    meta_id = Column(Integer, ForeignKey("metas_financeiras.id"), nullable=False)
    valor = Column(Float, nullable=False)
    descricao = Column(String, nullable=True)
    data_transacao = Column(Date, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", back_populates="transacoes_meta")
    meta = relationship("MetaFinanceira", back_populates="transacoes")

# Modelo para Investimentos
class Investimento(Base):
    __tablename__ = "investimentos"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    nome = Column(String, nullable=False)
    tipo = Column(Enum(TipoInvestimento), nullable=False)
    valor_investido = Column(Float, nullable=False)
    valor_atual = Column(Float, nullable=False)
    data_investimento = Column(Date, nullable=False)
    data_resgate = Column(Date, nullable=True)
    rentabilidade_anual = Column(Float, nullable=True)  # Taxa de rentabilidade anual
    observacoes = Column(Text, nullable=True)
    ativo = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    user = relationship("User", back_populates="investimentos")

# Modelo para Resumos Financeiros (para gráficos e relatórios)
class ResumoFinanceiro(Base):
    __tablename__ = "resumos_financeiros"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    mes = Column(Integer, nullable=False)
    ano = Column(Integer, nullable=False)
    total_receitas = Column(Float, default=0.0)
    total_despesas = Column(Float, default=0.0)
    saldo_mensal = Column(Float, default=0.0)
    total_investido = Column(Float, default=0.0)
    total_metas = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    user = relationship("User")
