def calculo_risco_atual(carteira):
    risco_atual = 0
    soma_valores = 0
    if len(carteira) > 0:
        for ativo in carteira:
            risco_atual += ativo["risco"] * ativo["valor_investido"]
            soma_valores += ativo["valor_investido"]
        risco_atual /= soma_valores
    return risco_atual

def risco_projetado(carteira, compra):
    compra_corrigida = compra.copy()
    compra_corrigida["valor_investido"] = compra_corrigida.pop("valor_ordem")

    carteira_nova = carteira + [compra_corrigida]
    novo_risco = calculo_risco_atual(carteira_nova)
    return novo_risco

def desenquadramento(perfil, carteira, compra):
    novo_risco = round(risco_projetado(carteira, compra), 2)
    score_maximo = perfil["score_max_risco"]

    if round(score_maximo * 1.1, 2) >= novo_risco:
        status = "Aprovado"
        mensagem = "Ordem executada. Carteira em conformidade."
    elif round(score_maximo * 1.2, 2) >= novo_risco:
        status = "Alerta"
        mensagem = f"Atenção: O risco da carteira ultrapassará o limite de {(score_maximo*1.1):.2f}. É necessário termo de ciência."
    else:
        status = "Rejeitado"
        mensagem = "Risco excessivo. A operação viola a política de Suitability."

    alerta = {"status": status, "risco_projetado": novo_risco, "mensagem": mensagem}
    return alerta

# FUNÇÃO MAIN

if __name__ == "__main__":
    import test_codigo

    perfil = {"perfil": "Moderado", "score_max_risco": 2.5}
    carteira = [
        {"ativo": "CDB XPTO", "risco": 1.2, "valor_investido": 50000},
        {"ativo": "Ação ABC", "risco": 4.0, "valor_investido": 10000},
    ]
    ordem = {"ativo": "FII YYY", "risco": 3.5, "valor_ordem": 5000}

    resultado = desenquadramento(perfil, carteira, ordem)
    print(resultado)

    funcoes = ["calculo_risco_atual", "risco_projetado", "desenquadramento"]

    for funcao in funcoes:
        aprovados = 0
        total = 0
        for nome_teste in dir(test_codigo):
            if nome_teste.startswith(f"test_{funcao}"):
                total += 1
                try:
                    getattr(test_codigo, nome_teste)()
                    aprovados += 1
                except AssertionError:
                    print(f"  falhou: {nome_teste}")
        print(f"{funcao} passou em {aprovados}/{total} testes")
