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
    novo_risco = risco_projetado(carteira, compra)
    score_maximo = perfil["score_max_risco"]

    if score_maximo * 1.1 >= novo_risco:
        status = "Aprovado"
        mensagem = "Ordem executada. Carteira em conformidade."
    elif score_maximo * 1.2 >= novo_risco:
        status = "Alerta"
        mensagem = f"Atenção: O risco da carteira ultrapassará o limite de {(score_maximo*1.1):.2f}. É necessário termo de ciência."
    else:
        status = "Rejeitado"
        mensagem = "Risco excessivo. A operação viola a política de Suitability."

    alerta = {"status": status, "risco_projetado": novo_risco, "mensagem": mensagem}
    return alerta