# Case I – Motor de Validação de Suitability de Carteira (CVM 30)

**Autor:** Caio Rosa

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

**Decisões tomadas:**

- **Limite de rejeição em 20%:** o enunciado define o gatilho do alerta (10% acima do score máximo), mas não diz onde começa o desenquadramento severo. Adotei 20% acima do score como limite. Esse valor fica centralizado na função e pode ser trocado facilmente se a política da Genial for outra.
- **Arredondamento:** o risco projetado é arredondado para 2 casas antes da comparação, como no formato de saída do enunciado. Os limites também são arredondados, para evitar erros de ponto flutuante (por exemplo, `2.5 * 1.1` dá `2.7500000000000004` em Python). Assim, um risco de exatamente 2.75 é aprovado, pois o alerta só dispara quando o limite é *ultrapassado*.

### Exemplo do enunciado

Carteira com CDB XPTO (risco 1.2, R$ 50.000) e Ação ABC (risco 4.0, R$ 10.000), mais uma ordem de FII YYY (risco 3.5, R$ 5.000):

```
(1.2 × 50000 + 4.0 × 10000 + 3.5 × 5000) / 65000 = 117500 / 65000 ≈ 1.81
```

```json
{"status": "Aprovado", "risco_projetado": 1.81, "mensagem": "Ordem executada. Carteira em conformidade."}
```

### Como executar

```bash
pip install -r requirements.txt
python codigo.py        # roda o exemplo do enunciado e mostra o resultado dos testes por função
pytest test_codigo.py   # roda a suíte de testes com o pytest
```

Os testes em [`test_codigo.py`](test_codigo.py) cobrem os três status, a carteira vazia, as fronteiras exatas (2.75 e 3.00) e garantem que a carteira e a ordem originais não são modificadas.

---

## 2. Regulação vs. Negócio: cliente que prossegue após o Alerta

Quando o cliente recebe o Alerta e decide seguir com a compra assinando o Termo de Ciência, a Genial precisa conseguir provar depois, para a CVM, para a auditoria ou num eventual processo, que o cliente foi avisado e aceitou o risco conscientemente. Isso traz implicações tanto de tecnologia quanto de compliance.

### Implicações tecnológicas

- **Registro do Termo de Ciência no banco de dados:** cada aceite deve ser salvo com o ID do cliente, o ID da ordem, a data e hora, o texto exato do termo apresentado (ou a versão dele), o risco projetado, o score máximo do perfil e o status retornado pelo motor. Guardar o texto ou a versão é importante porque o termo pode mudar com o tempo, e é preciso saber exatamente o que o cliente leu.
- **Log de auditoria imutável:** toda execução do motor deve ser registrada, e não só os alertas aceitos. Isso inclui as entradas (perfil, carteira, ordem), a saída e a versão do código ou das regras usadas. O log deve ser append-only (não pode ser editado nem apagado) e guardado pelo prazo exigido pela regulação, que na CVM 30 é de no mínimo 5 anos.
- **Evidência da autenticação do cliente:** registrar como o cliente confirmou o aceite (login, senha de assinatura eletrônica, token, IP, dispositivo e canal: app, web ou assessor), para que o aceite não possa ser contestado.
- **Vínculo entre o aceite e a ordem:** a ordem só pode ser enviada para execução se existir um termo válido ligado a ela. Se o cliente fechar o app no meio do fluxo, a ordem não pode ser executada. Também vale revalidar o risco no momento da execução, já que preços e carteira podem mudar entre o alerta e o envio.
- **Separação clara entre Alerta e Rejeição:** o sistema não pode permitir que um termo de ciência "destrave" uma ordem Rejeitada. Essa regra deve ser garantida no backend, e não só escondendo o botão no app.
- **Versionamento das regras:** os limites (10% e 20%) e o score de cada perfil podem mudar. Cada decisão deve registrar qual versão da regra foi aplicada, para que seja possível reproduzir a decisão depois.

### Implicações de compliance

- **Comprovação perante a CVM:** em uma fiscalização, a Genial precisa mostrar que avisou o cliente de forma clara antes da operação. O registro do termo e o log são essa prova.
- **Linguagem clara no termo:** o termo deve explicar em linguagem simples qual é o risco, quanto a carteira vai ultrapassar o perfil e o que isso significa, e não ser só uma caixa de "li e aceito".
- **Monitoramento de padrões:** compliance deve acompanhar relatórios de clientes que aceitam termos com frequência, ou de assessores cujos clientes aceitam muitos termos. Isso pode indicar que o perfil do cliente está desatualizado ou que há um problema de conduta na recomendação.
- **Sugestão de atualização de perfil:** se o cliente aceita alertas repetidamente, é um sinal de que o questionário de suitability talvez não reflita mais a realidade dele. O sistema pode sugerir que ele refaça o questionário.
- **Proteção de dados (LGPD):** esses registros têm dados pessoais e financeiros, então precisam de controle de acesso, criptografia e uma política de retenção definida.

---

## 3. Desenquadramento Passivo

O desenquadramento passivo acontece quando a carteira sai do perfil sem que o cliente tenha feito nada, por exemplo quando uma ação de risco alto valoriza muito e passa a pesar mais na carteira, ou quando o risco de um ativo é reclassificado.

### Como usar o motor

O motor já tem o que é preciso: a função `calculo_risco_atual` calcula o risco da carteira como ela está hoje. A diferença é que, em vez de rodar antes de uma compra, ela rodaria periodicamente sobre todas as carteiras:

1. **Rotina diária (batch):** após o fechamento do mercado, um job pega a posição de cada cliente com os preços atualizados (`valor_investido` passa a ser o valor de mercado atual) e roda `calculo_risco_atual`. Depois compara o resultado com o `score_max_risco` do perfil usando as mesmas faixas do motor (dentro do perfil, desenquadramento leve, desenquadramento severo). Dá para reaproveitar a lógica de `desenquadramento` tratando a carteira atual como a projetada.
2. **Gatilhos por evento:** além da rotina diária, o cálculo pode rodar quando acontece algo relevante, como uma variação forte de preço de um ativo, a reclassificação de risco de um produto ou uma mudança no perfil do cliente. Assim o problema é detectado no mesmo dia, sem esperar o fechamento.
3. **Evitar notificações repetidas:** salvar o último status de cada carteira e só notificar quando o status *muda* (por exemplo, de Aprovado para Alerta). Sem isso, o cliente receberia o mesmo aviso todo dia e passaria a ignorar.
4. **Histórico:** gravar o risco calculado de cada carteira ao longo do tempo. Isso serve como evidência para a auditoria de que a Genial monitora as carteiras, e permite ver a tendência (por exemplo, uma carteira que está se aproximando do limite).
5. **Sugestão de reenquadramento:** junto com o aviso, o sistema pode sugerir ações para voltar ao perfil, como quanto vender do ativo que mais pesa no risco ou quanto aplicar em ativos de risco baixo. Isso pode ser simulado com a própria função `risco_projetado`.

### Canais de comunicação

O canal deve depender da gravidade do desenquadramento:

| Situação | Canais | Por quê |
|---|---|---|
| **Leve** (faixa de Alerta) | Notificação push no app + aviso dentro do app | É rápido e o cliente já está no app para agir. Dentro do app dá para mostrar o detalhe do risco e um atalho para rebalancear. |
| **Severo** (faixa de Rejeição) | App + e-mail + contato do assessor | É a situação mais crítica. O e-mail serve como registro formal de que o cliente foi informado, e o assessor consegue explicar a situação e ajudar na decisão. |
| **Persistente** (carteira fora do perfil há vários dias sem ação) | Assessor | Se o cliente ignorou os avisos automáticos, o contato humano é o mais eficaz para resolver. |

Na minha avaliação, o **app** é o canal mais eficaz para o dia a dia, porque é imediato e permite que o cliente resolva na hora. O **e-mail** é importante como registro formal para compliance, mesmo tendo menos leitura. E o **assessor** é o mais eficaz nos casos graves, porque consegue conversar com o cliente e entender se ele quer rebalancear a carteira ou atualizar o perfil. Para clientes sem assessor, um alerta no app que exige confirmação de leitura pode cumprir esse papel.

Assim como no caso do Alerta ativo, todo envio de notificação deve ser registrado (canal, data e hora, conteúdo e se foi lido), para comprovar que a Genial informou o cliente.
