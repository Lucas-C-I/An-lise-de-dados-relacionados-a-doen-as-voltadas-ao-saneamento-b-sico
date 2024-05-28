import json
from dash import Dash, html, dcc, callback, Output, Input, dash_table, State
from waitress import serve
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import requests

url = "https://apisidra.ibge.gov.br/values/t/354/g/2/v/allxp/p/all/c12963/all?formato=json"

light_icon_theme = "assets/img/sun.png"
night_icon_theme = "assets/img/moon.png"

with open("brasil_estados.json", "r", encoding="utf-8") as f:
    geojson = json.load(f)

response = requests.get(url)
data = response.json()
df = pd.DataFrame(data)

df.columns = df.iloc[0]
df = df.drop(0)

df["Tipo de doença"] = df["Tipo de doença"].replace(
    "Doença do aparelho respiratório", "DAR*"
)

novo_df = df.loc[~df["Tipo de doença"].isin(["Total", "Total geral de municípios"])]

novo_df = novo_df.sort_values(by="Tipo de doença")

novo_df = novo_df[
    [
        "Tipo de doença",
        "Nível Territorial",
        "Valor",
        "Ano",
        "Brasil, Grande Região e UF",
        "Tipo de doença (Código)",
    ]
]


drop_estados = ["Brasil", "Norte", "Nordeste", "Sudeste", "Sul", "Centro-Oeste"]
df["estados"] = novo_df["Brasil, Grande Região e UF"]
mascara = ~df["estados"].isin(drop_estados)

estados_unique = df[mascara]["estados"].unique()

df_estados = []
for feature in geojson["features"]:
    name = feature["properties"]["name"]
    if name in estados_unique:
        sigla = feature["id"]
        df_estados.append({"ID": sigla, "Nome": name})

df_estados = pd.DataFrame(df_estados)

df_final = pd.merge(
    novo_df,
    df_estados,
    left_on="Brasil, Grande Região e UF",
    right_on="Nome",
    how="left",
)

df_final.dropna(subset=["Nome"], inplace=True)
df_final.rename(columns={"Nome": "Estados", "ID": "UF"}, inplace=True)

df_final = (
    df_final.drop("Nível Territorial", axis=1)
    .drop("Tipo de doença (Código)", axis=1)
    .drop("Brasil, Grande Região e UF", axis=1)
)
df_final["Valor"] = df_final["Valor"].replace("-", 0)
df_final["Valor"] = df_final["Valor"].astype(int)


app = Dash(__name__)

server = app.server

app.layout = [
    html.Title('Doenças Relacionadas a Falta de Saneamento Básico - IBGE'),
    html.Div(
        [
            html.H1(
                children="Doenças Relacionadas a Falta de Saneamento Básico - IBGE",
                style={"textAlign": "center"},
            ),
            html.Img(src=light_icon_theme, alt="theme-btn", id="theme-img", className="theme-img"),
            html.Link(rel='stylesheet', id='theme-css', href='assets/light-style.css')
        ], id='title-content'
    ),
    html.Div(
        [
            html.H2(children="Doenças por Estado", style={"textAlign": "center"}),
            dcc.Dropdown(
                options=df_estados["Nome"],
                value="Acre",
                id="uf-dropdown",
                clearable=True,
                className="dropdown-style",
            ),
            dcc.Graph(figure={}, id="graph-content"),
        ],
        id="histogram-content",
    ),
    html.Div(
        [
            html.Div(
                [
                    html.H2(
                        children="Quantidade de Doenças por Tipo e Estado",
                        style={"textAlign": "center"},
                    ),
                    dash_table.DataTable(
                        page_size=20,
                        id="datatable-content",
                        style_header={
                            "backgroundColor": "rgb(30, 30, 30)",
                            "color": "white",
                            "textAlign": "center",
                        },
                        style_data={
                            "backgroundColor": "rgb(50, 50, 50)",
                            "color": "white",
                            "textAlign": "center",
                        },
                    ),
                ],
                id="table-content",
            ),
            html.Div(
                [
                    html.H2(
                        children="Prevalência de Doenças por Estado",
                        style={"textAlign": "center"},
                    ),
                    dcc.Dropdown(
                        options=[
                            doenca for doenca in df_final["Tipo de doença"].unique()
                        ],
                        value="Cólera",
                        id="dropdown-map-filter",
                        className="dropdown-style",
                    ),
                    html.Div(id="map-content"),
                ],
                id="drop-map-content",
            ),
        ],
        id="first-div",
    ),
    html.Div(html.H5(children="* DAR - Doenças do Aparelho Respiratório")),
]

@app.callback(
    Output("theme-img", "src"),
    [Input("theme-img", "n_clicks")],
    [State("theme-img", "src")]
)
def toggle_theme(n_clicks, current_src):
    if current_src == light_icon_theme:
        return night_icon_theme
    else:
        return light_icon_theme
    
@app.callback(
    Output("theme-css", "href"),
    [Input("theme-img", "n_clicks")],
    [State("theme-img", "src")]
)
def update_css(n_clicks, current_src):
    theme = "light-style" if current_src == light_icon_theme else "dark-style"
    return f"assets/{theme}.css"    

@app.callback(Output("datatable-content", "data"), Input("uf-dropdown", "value"))
def update_table(value):
    dff = novo_df[novo_df["Brasil, Grande Região e UF"] == value]
    dff = dff.drop("Brasil, Grande Região e UF", axis=1).drop(
        "Tipo de doença (Código)", axis=1
    )
    dff = dff.rename(columns={"Valor": "Quantidade de Casos"})
    return dff.to_dict("records")


theme_changed = False

@app.callback(
    Output("graph-content", "figure"),
    [Input('uf-dropdown', 'value'), Input("theme-img", "n_clicks")], [State("theme-img", "src")]
)
def update_histogram(value, n_clicks, current_src):
    dff = novo_df[novo_df["Brasil, Grande Região e UF"] == value]
    global theme_changed

    if n_clicks is not None and n_clicks % 2 == 0:
        theme_changed = False
    elif n_clicks is not None:
        theme_changed = True
    
    template = "plotly_dark" if theme_changed else "plotly"
    fig = px.histogram(
        dff, x="Tipo de doença", y="Valor", text_auto=True, template=template
    )
    return fig



@app.callback(Output("map-content", "children"), [Input("dropdown-map-filter", "value"), Input("theme-img", "n_clicks")], [State("theme-img", "src")])
def update_map(selected_option,  n_clicks,current_src):    
    global theme_changed

    if n_clicks is not None and n_clicks % 2 == 0:
        theme_changed = False
    elif n_clicks is not None:
        theme_changed = True
    
    feltred_df = df_final[df_final["Tipo de doença"] == selected_option]
    
    template = "plotly_dark" if theme_changed else "plotly"

    fig = px.choropleth(
        feltred_df,
        geojson=geojson,
        locations="UF",
        range_color=(df_final["Valor"].min(), df_final["Valor"].max()),
        hover_data=["UF"],
        scope="south america",
        color="Valor",
        color_continuous_scale="Reds",
        template=template,
    )

    return dcc.Graph(figure=fig, className="map-graph")


if __name__ == "__main__":
    serve(app.server, host='127.0.0.1', port=8050)
