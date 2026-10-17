# genial-case-caio-rosa

Motor de Validação de Suitability de Carteira (CVM 30), feito para o Case I do Programa de Estágio de Férias da Genial Investimentos.

As respostas do relatório estão em [`case-report.md`](case-report.md).

## Arquivos

- [`codigo.py`](codigo.py): o motor (cálculo do risco atual, risco projetado e validação do desenquadramento)
- [`test_codigo.py`](test_codigo.py): testes das três funções
- [`case-report.md`](case-report.md): relatório com as respostas do case

## Como executar

```bash
pip install -r requirements.txt
python codigo.py        # roda o exemplo do enunciado e mostra o resultado dos testes por função
pytest test_codigo.py   # roda a suíte de testes com o pytest
```

Os testes cobrem os três status, a carteira vazia, as fronteiras exatas (2.75 e 3.00) e garantem que a carteira e a ordem originais não são modificadas.
