import copy

import pytest

from codigo import calculo_risco_atual, desenquadramento, risco_projetado

PERFIL_MODERADO = {"perfil": "Moderado", "score_max_risco": 2.5}

CARTEIRA_ENUNCIADO = [
    {"ativo": "CDB XPTO", "risco": 1.2, "valor_investido": 50000},
    {"ativo": "Ação ABC", "risco": 4.0, "valor_investido": 10000},
]
ORDEM_ENUNCIADO = {"ativo": "FII YYY", "risco": 3.5, "valor_ordem": 5000}


# --- calculo_risco_atual ---

def test_calculo_risco_atual_carteira_simples():
    # (1.0*30000 + 4.0*10000) / 40000 = 70000 / 40000 = 1.75
    carteira = [
        {"ativo": "A", "risco": 1.0, "valor_investido": 30000},
        {"ativo": "B", "risco": 4.0, "valor_investido": 10000},
    ]
    assert calculo_risco_atual(carteira) == pytest.approx(1.75)


def test_calculo_risco_atual_carteira_de_um_ativo():
    carteira = [{"ativo": "A", "risco": 3.2, "valor_investido": 15000}]
    assert calculo_risco_atual(carteira) == pytest.approx(3.2)


def test_calculo_risco_atual_carteira_vazia_retorna_zero():
    assert calculo_risco_atual([]) == 0


# --- risco_projetado ---

def test_risco_projetado_exemplo_do_enunciado():
    # (1.2*50000 + 4.0*10000 + 3.5*5000) / 65000 = 117500 / 65000 ≈ 1.8077
    assert risco_projetado(CARTEIRA_ENUNCIADO, ORDEM_ENUNCIADO) == pytest.approx(1.81, abs=0.005)


def test_risco_projetado_carteira_vazia_igual_ao_risco_do_ativo():
    ordem = {"ativo": "FII YYY", "risco": 3.5, "valor_ordem": 5000}
    assert risco_projetado([], ordem) == pytest.approx(3.5)


def test_risco_projetado_nao_modifica_carteira_nem_ordem():
    carteira = copy.deepcopy(CARTEIRA_ENUNCIADO)
    ordem = copy.deepcopy(ORDEM_ENUNCIADO)

    risco_projetado(carteira, ordem)

    assert carteira == CARTEIRA_ENUNCIADO
    assert ordem == ORDEM_ENUNCIADO


# --- desenquadramento ---

def test_desenquadramento_aprovado_exemplo_do_enunciado():
    resultado = desenquadramento(PERFIL_MODERADO, CARTEIRA_ENUNCIADO, ORDEM_ENUNCIADO)
    assert resultado["status"] == "Aprovado"
    # O contrato pede risco_projetado arredondado a 2 casas
    assert resultado["risco_projetado"] == 1.81


def test_desenquadramento_alerta():
    # (1.2*50000 + 4.5*50000) / 100000 = 2.85 → entre 2.75 e 3.0
    carteira = [{"ativo": "CDB XPTO", "risco": 1.2, "valor_investido": 50000}]
    ordem = {"ativo": "Ação DEF", "risco": 4.5, "valor_ordem": 50000}
    resultado = desenquadramento(PERFIL_MODERADO, carteira, ordem)
    assert resultado["status"] == "Alerta"
    assert "2.75" in resultado["mensagem"]


def test_desenquadramento_rejeitado():
    # (1.2*10000 + 5.0*40000) / 50000 = 4.24 → acima de 3.0
    carteira = [{"ativo": "CDB XPTO", "risco": 1.2, "valor_investido": 10000}]
    ordem = {"ativo": "Cripto ZZZ", "risco": 5.0, "valor_ordem": 40000}
    resultado = desenquadramento(PERFIL_MODERADO, carteira, ordem)
    assert resultado["status"] == "Rejeitado"


def test_desenquadramento_fronteira_exatamente_2_75_aprovado():
    # (2.0*30000 + 5.0*10000) / 40000 = 110000 / 40000 = 2.75 = 2.5 * 1.1
    carteira = [{"ativo": "A", "risco": 2.0, "valor_investido": 30000}]
    ordem = {"ativo": "B", "risco": 5.0, "valor_ordem": 10000}
    resultado = desenquadramento(PERFIL_MODERADO, carteira, ordem)
    assert resultado["status"] == "Aprovado"


def test_desenquadramento_fronteira_exatamente_3_00_alerta():
    # (2.0*20000 + 5.0*10000) / 30000 = 90000 / 30000 = 3.0 = 2.5 * 1.2
    carteira = [{"ativo": "A", "risco": 2.0, "valor_investido": 20000}]
    ordem = {"ativo": "B", "risco": 5.0, "valor_ordem": 10000}
    resultado = desenquadramento(PERFIL_MODERADO, carteira, ordem)
    assert resultado["status"] == "Alerta"
