# dashboard_llama3_mall.py

import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html, Input, Output
import requests
import json
import dash_bootstrap_components as dbc
import os

# Cargar el dataset de clientes del mall
df = pd.read_csv("https://raw.githubusercontent.com/EdwinAAH/Inteligencia-de-negocios/refs/heads/main/Mall_Customers.csv")

# Inicializar la app de Dash con tema pastel (Minty)
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.MINTY])
app.title = "Dashboard de Clientes del Mall + LLaMA 3"

# Layout del dashboard
app.layout = dbc.Container([
    html.H1("Dashboard de Segmentación de Clientes", className="text-center my-4"),

    dbc.Row([
        dbc.Col([
            html.Label("Género"),
            dcc.Dropdown(
                id='gender-filter',
                options=[{'label': g, 'value': g} for g in df['Gender'].unique()],
                multi=True,
                placeholder="Selecciona género(s)"
            )
        ], md=4),
        dbc.Col([
            html.Label("Edad mínima"),
            dcc.Slider(id='age-slider', min=df['Age'].min(), max=df['Age'].max(),
                       step=1, value=df['Age'].min(),
                       marks={i: str(i) for i in range(df['Age'].min(), df['Age'].max()+1, 10)})
        ], md=4),
        dbc.Col([
            html.Label("Pregunta a LLaMA 3"),
            dcc.Textarea(
                id='user-question',
                placeholder='Ej. ¿Qué tipo de cliente gasta más?',
                style={'width': '100%', 'height': 80}
            ),
            html.Br(),
            html.Button('Preguntar a la IA', id='ask-button', n_clicks=0, className='btn btn-primary'),
            html.Div(id='llama-response', className='mt-3', style={'whiteSpace': 'pre-wrap'})
        ], md=4),
    ], className='mb-4'),

    dbc.Row([
        dbc.Col(dcc.Graph(id='scatter-income-score'), md=6),
        dbc.Col(dcc.Graph(id='boxplot-score'), md=6)
    ]),

    dbc.Row([
        dbc.Col(dcc.Graph(id='hist-age'), md=6),
        dbc.Col(dcc.Graph(id='bar-gender-count'), md=6)
    ]),

], fluid=True)

# Callback para actualizar las gráficas
@app.callback(
    [Output('scatter-income-score', 'figure'),
     Output('boxplot-score', 'figure'),
     Output('hist-age', 'figure'),
     Output('bar-gender-count', 'figure')],
    [Input('gender-filter', 'value'),
     Input('age-slider', 'value')]
)
def update_graphs(selected_gender, min_age):
    filtered_df = df.copy()
    if selected_gender:
        filtered_df = filtered_df[filtered_df['Gender'].isin(selected_gender)]
    if min_age:
        filtered_df = filtered_df[filtered_df['Age'] >= min_age]

    scatter_fig = px.scatter(filtered_df, x='Annual Income (k$)', y='Spending Score (1-100)',
                             color='Gender', title='Ingreso vs Puntuación de Gasto',
                             labels={'Annual Income (k$)': 'Ingreso Anual (k$)', 'Spending Score (1-100)': 'Puntaje de Gasto'})

    boxplot_fig = px.box(filtered_df, x='Gender', y='Spending Score (1-100)',
                         title='Distribución del Gasto por Género')

    hist_fig = px.histogram(filtered_df, x='Age', nbins=10,
                            title='Distribución de Edad')

    bar_fig = px.histogram(filtered_df, x='Gender',
                           title='Cantidad de Clientes por Género')

    return scatter_fig, boxplot_fig, hist_fig, bar_fig

# Callback para hacer pregunta a LLaMA 3
@app.callback(
    Output('llama-response', 'children'),
    Input('ask-button', 'n_clicks'),
    Input('user-question', 'value')
)
def ask_llama3(n_clicks, question):
    if n_clicks > 0 and question:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": "Bearer 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",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "llama3-8b-8192",
            "messages": [
                {"role": "system", "content": "Eres un experto en análisis de clientes de centros comerciales."},
                {"role": "user", "content": question}
            ]
        }
        try:
            response = requests.post(url, headers=headers, data=json.dumps(payload))
            result = response.json()
            return result['choices'][0]['message']['content']
        except Exception as e:
            return f"Error al consultar LLaMA 3: {e}"
    return ""

# Ejecutar app
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8050))
    app.run(host="0.0.0.0", port=port, debug=True)


#Ejemplo