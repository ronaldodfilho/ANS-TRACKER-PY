from dataclasses import dataclass, field
from typing import List


@dataclass
class Alteracao:
    registro_ans: str
    razao_social: str
    campo: str
    valor_anterior: str
    valor_atual: str

    def eh_critica(self, campos_criticos: list) -> bool:
        return self.campo in campos_criticos


@dataclass
class Inconsistencia:
    registro_ans: str
    razao_social: str
    tipo: str
    descricao: str


@dataclass
class ResumoDiff:
    periodo_anterior: str
    periodo_atual: str
    adicionados: List[dict] = field(default_factory=list)
    removidos: List[dict] = field(default_factory=list)
    alteracoes: List[Alteracao] = field(default_factory=list)
    inconsistencias: List[Inconsistencia] = field(default_factory=list)

    @property
    def alteracoes_criticas(self) -> List[Alteracao]:
        from config import COLUNAS_CRITICAS
        return [a for a in self.alteracoes if a.eh_critica(COLUNAS_CRITICAS)]

    def total_mudancas(self) -> int:
        return len(self.adicionados) + len(self.removidos) + len(self.alteracoes)