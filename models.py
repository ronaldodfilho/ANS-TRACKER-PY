from dataclasses import dataclass
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