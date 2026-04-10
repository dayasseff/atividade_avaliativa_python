from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI()

# --- MODELOS DE DADOS ---
# Desenvolvedor e Projeto
class Desenvolvedor(BaseModel):
    id: Optional[int] = None
    nome: str
    senioridade: str
    pontos_por_dia: int
    linguagem: str

class Projeto(BaseModel):
    id: Optional[int] = None
    descricao: str
    prazo_dias: int
    pontos_funcao: int
    desenvolvedores_ids: List[int] = []

# "Bancos de Dados" temporários (listas na memória)
db_desenvolvedores = []
db_projetos = []

# --- MÉTODOS DA API ---

# 1. Cadastrar Desenvolvedor
@app.post("/desenvolvedores")
def cadastrar_dev(dev: Desenvolvedor):
    dev.id = len(db_desenvolvedores) + 1
    db_desenvolvedores.append(dev)
    return dev

# 2. Listar todos os Desenvolvedores
@app.get("/desenvolvedores")
def listar_devs():
    return db_desenvolvedores

# 3. Criar Novo Projeto
@app.post("/projetos")
def criar_proj(proj: Projeto):
    proj.id = len(db_projetos) + 1
    db_projetos.append(proj)
    return proj

# 4. Listar todos os Projetos
@app.get("/projetos")
def listar_projs():
    return db_projetos

# 5. Vincular um Desenvolvedor a um Projeto
@app.post("/projetos/{projeto_id}/desenvolvedores")
def vincular_dev(projeto_id: int, corpo: dict):
    projeto = next((p for p in db_projetos if p.id == projeto_id), None)
    if not projeto:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")
    
    dev_id = corpo.get("desenvolvedor_id")
    projeto.desenvolvedores_ids.append(dev_id)
    return {"mensagem": "Desenvolvedor alocado com sucesso!"}

# 6. Verificar Viabilidade (Cálculo solicitado no README)
@app.get("/projetos/{projeto_id}/viabilidade")
def verificar_viabilidade(projeto_id: int):
    projeto = next((p for p in db_projetos if p.id == projeto_id), None)
    if not projeto:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")
    
    # Soma os pontos/dia de todos os devs vinculados
    soma_pontos = 0
    for d_id in projeto.desenvolvedores_ids:
        dev = next((d for d in db_desenvolvedores if d.id == d_id), None)
        if dev:
            soma_pontos += dev.pontos_por_dia
    
    # Regra: Capacidade = (Soma pontos) * Prazo em dias
    capacidade_total = soma_pontos * projeto.prazo_dias
    viavel = capacidade_total >= projeto.pontos_funcao
    
    return {
        "projeto": projeto.descricao,
        "viabilidade": "Projeto Viável" if viavel else "Projeto Inviável",
        "capacidade_maxima": capacidade_total,
        "pontos_necessarios": projeto.pontos_funcao
    }

