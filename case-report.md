# Case I – Motor de Validação de Suitability de Carteira (CVM 30)

**Autor:** Caio Rosa

> As instruções para executar o código e os testes estão no [README](README.md).

## 1. Implementação

O motor está em [`codigo.py`](codigo.py) e é dividido em três funções, uma para cada etapa pedida no enunciado:

| Função | O que faz |
|---|---|
| `calculo_risco_atual(carteira)` | Calcula o risco da carteira pela média ponderada do risco de cada ativo pelo valor investido. Para uma carteira vazia, retorna 0. |
| `risco_projetado(carteira, compra)` | Junta a nova ordem à carteira (sem alterar os dados originais) e recalcula o risco com a função acima. |
| `desenquadramento(perfil, carteira, compra)` | Compara o risco projetado com o score máximo do cliente e devolve o dicionário com `status`, `risco_projetado` e `mensagem`. |

### Regras de decisão

Com `score_max` sendo o score máximo de risco do perfil:

| Status | Condição | Exemplo (Moderado, 2.5) |
|---|---|---|
| Aprovado | risco projetado ≤ `score_max × 1.1` | até 2.75 |
| Alerta | `score_max × 1.1` < risco projetado ≤ `score_max × 1.2` | entre 2.75 e 3.00 |
| Rejeitado | risco projetado > `score_max × 1.2` | acima de 3.00 |

### Observação
Foi adotado o valor de score_max * 1.2 pra diferenciar se é alerta ou rejeitado, visto que o enunciado não especificou.

### Exemplo do enunciado

Carteira com CDB XPTO (risco 1.2, R$ 50.000) e Ação ABC (risco 4.0, R$ 10.000), mais uma ordem de FII YYY (risco 3.5, R$ 5.000):

```
(1.2 × 50000 + 4.0 × 10000 + 3.5 × 5000) / 65000 = 117500 / 65000 ≈ 1.81
```

```json
{"status": "Aprovado", "risco_projetado": 1.81, "mensagem": "Ordem executada. Carteira em conformidade."}
```

---

## 2. Regulação vs. Negócio: cliente que prossegue após o Alerta

Quando o cliente recebe o Alerta e decide seguir com a compra assinando o Termo de Ciência, a Genial precisa conseguir provar depois, para a CVM, para a auditoria ou num eventual processo, que o cliente foi avisado e aceitou o risco conscientemente. Isso traz implicações tanto de tecnologia quanto de compliance.

### Implicações tecnológicas

- **Salvar o Termo de Ciência:** guardar no banco de dados quem aceitou, qual ordem, quando, qual foi o risco calculado e o texto do termo que o cliente viu.
- **Registro de todas as validações:** toda vez que o motor roda, salvar o que entrou e o resultado. Esses registros não podem ser editados nem apagados, para servirem como prova numa auditoria.
- **Ordem só sai com o termo aceito:** se o cliente fechar o app antes de aceitar, a compra não acontece. E uma ordem Rejeitada nunca pode ser liberada por um termo, mesmo que alguém tente burlar o app.

### Implicações de compliance

- **Prova para a CVM:** numa fiscalização, a Genial precisa mostrar que avisou o cliente antes da compra. Os registros acima são essa prova.
- **Termo fácil de entender:** o aviso deve explicar de forma simples o risco que o cliente está assumindo, e não ser só um "li e aceito".
- **Acompanhar quem aceita muitos alertas:** se um cliente aceita alertas com frequência, talvez o perfil dele esteja desatualizado, e vale sugerir que ele refaça o questionário de suitability.

---

## 3. Desenquadramento Passivo

O desenquadramento passivo acontece quando a carteira sai do perfil sem o cliente fazer nada, por exemplo quando uma ação arriscada valoriza muito e passa a ocupar uma fatia maior da carteira.

### Como usar o motor

A função `calculo_risco_atual` já calcula o risco da carteira como ela está hoje. Basta rodá-la regularmente para todos os clientes:

1. **Uma vez por dia:** depois que o mercado fecha, recalcular o risco de cada carteira com os preços atualizados e comparar com o perfil do cliente, usando as mesmas faixas do motor (Aprovado, Alerta e Rejeitado).
2. **Avisar só quando mudar:** guardar o último resultado de cada carteira e só notificar quando ele piorar (por exemplo, de Aprovado para Alerta). Assim o cliente não recebe o mesmo aviso todo dia.
3. **Sugerir uma solução:** junto com o aviso, mostrar o que o cliente pode fazer para voltar ao perfil, como vender parte do ativo mais arriscado. Dá para simular isso com a própria função `risco_projetado`.

### Canais de comunicação

| Situação | Canal | Por quê |
|---|---|---|
| **Leve** (faixa de Alerta) | Notificação no app | É rápido e o cliente já consegue resolver ali mesmo. |
| **Grave** (faixa de Rejeição) | App + e-mail + assessor | O e-mail fica como registro formal, e o assessor consegue explicar a situação e ajudar o cliente a decidir. |
| **Cliente não respondeu** aos avisos | Assessor | Quando os avisos automáticos são ignorados, o contato pessoal é o que mais funciona. |

Na minha avaliação, o **app** é o melhor canal para o dia a dia, o **e-mail** serve principalmente como comprovante, e o **assessor** é o mais eficaz nos casos graves. Em todos os casos, o envio do aviso também deve ser registrado, para provar que o cliente foi informado.
