# Sanitation Health Analysis

Este é um projeto de aplicativo web construído com Dash e Plotly, usado para visualizar dados relacionados a doenças relacionadas ao saneamento básico no Brasil, com base nos dados do IBGE.

## Funcionalidades Principais

- **Visualização de Dados:** O aplicativo permite visualizar dados sobre doenças relacionadas ao saneamento básico em diferentes estados do Brasil.
- **Histograma Interativo:** Um histograma interativo exibe a distribuição das doenças por tipo.
- **Mapa de Calor:** Um mapa de calor interativo mostra a prevalência das doenças em cada estado do Brasil.

## Instalação

Para executar o aplicativo localmente, siga estas etapas:

1. Clone este repositório em sua máquina local usando `git clone`.
2. Navegue até o diretório do projeto.
3. Instale as dependências listadas no arquivo `requirements.txt` executando `pip install -r requirements.txt`.
4. Execute o aplicativo com o comando `python app.py`.
5. Abra o navegador da web e acesse `http://localhost:8050` para visualizar o aplicativo.

## Tecnologias Utilizadas

- Python
- Dash
- Plotly
- Pandas
- Requests

## Estrutura do Projeto

```
├── app.py
├── assets
│   ├── css
│   │   ├── light-style.css
│   │   └── dark-style.css
│   └── img
│       ├── sun.png
│       └── moon.png
├── brasil_estados.json
├── README.md
└── requirements.txt
```
