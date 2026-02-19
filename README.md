# Validador de Dados (Data Reconciliation)

Este projeto é uma ferramenta de automação desenvolvida em Python para reconciliação e auditoria de bases de dados. Comparando um arquivo de entrada (Carga) contra uma base de referência (Sistema), ele identifica discrepâncias cadastrais de forma configurável e robusta.

## � Novidades da Versão

- **Interface Web Moderna**: Agora conta com uma interface desenvolvida em Streamlit para facilitar o uso por não-programadores.
- **Upload Dinâmico**: Permite carregar arquivos diretamente pelo navegador sem precisar movê-los para pastas específicas.
- **Métricas em Tempo Real**: Visualize a taxa de sucesso e o total de erros antes mesmo de baixar o relatório.
- **Modularização**: O núcleo de processamento foi separado (`main.py`) da interface (`app.py`) para maior flexibilidade.

## �🛠 Tecnologias Utilizadas

- **Python 3**: Linguagem base.
- **Pandas**: Biblioteca para manipulação e análise de dados.
- **Streamlit**: Framework para criação da interface web interativa.
- **OpenPyXL**: Leitura e escrita de arquivos Excel.

## 📂 Estrutura do Projeto

```
/
├── app.py                  # Interface Web (Streamlit)
├── main.py                 # Núcleo de processamento e CLI
├── settings.json           # Arquivo de configuração de regras
├── requirements.txt        # Dependências do projeto
├── dados/                  # Pasta opcional para arquivos locais
├── processamento.log       # Log detalhado da execução
└── README.md               # Documentação
```

## ▶️ Como Executar

Primeiro, instale as dependências necessárias:
```bash
pip install -r requirements.txt
```

### Opção 1: Interface Web (Recomendado)
Para abrir o painel visual no seu navegador:
```bash
streamlit run app.py
```
1.  Faça o upload dos arquivos de **Carga** e **Sistema**.
2.  (Opcional) Carregue um arquivo `settings.json` personalizado na barra lateral.
3.  Clique em "Iniciar Validação".
4.  Visualize as métricas e baixe o relatório corrigido.

### Opção 2: Linha de Comando (CLI)
Para executar via terminal de forma automatizada:
1.  Configure os caminhos dos arquivos no `settings.json`.
2.  Execute:
    ```bash
    python main.py
    ```
3.  Os resultados serão salvos automaticamente conforme definido no arquivo de configuração (`analise.xlsx` e `relatorio_inconsistencias.txt`).

## ⚙️ Configuração (`settings.json`)

O arquivo `settings.json` define as regras de negócio para a validação. Você pode editá-lo para adicionar novas colunas de verificação.

Exemplo:
```json
{
    "validacoes": [
        { "nome_verificacao": "VerificaCPF", "colunas_chave": ["CPF"] },
        { "nome_verificacao": "VerificaNome", "colunas_chave": ["CPF", "Nome"] }
    ],
    "validacao_final": {
        "nome_coluna": "Resultado",
        "colunas_chave": ["CPF", "Nome", "Matricula"]
    }
}
```