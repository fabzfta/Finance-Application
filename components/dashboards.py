from dash import html, dcc
from dash.dependencies import Input, Output, State
from datetime import date, datetime, timedelta
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import calendar
from globals import *
from app import app

card_icon = {
    "color":"white",
    "textAlign": "center",
    "fontSize": 30,
    "margin": "auto",

}

graph_margin = {'l': 25, 'r':25, 't':25, 'b':0}

# =========  Layout  =========== #
layout = dbc.Col([
    dbc.Row([
        dbc.Col([
            dbc.CardGroup([
                dbc.Card([
                    html.Legend('Saldo'),
                    html.H5('R$ 5400', id='p-saldo-dashboards', style={})        
                ], style = {'padding-left':'20px','padding-top':'10px'}),
                dbc.Card(
                    html.Div(className='fa fa-university', style=card_icon), 
                    color='warning',
                    style={'maxwidth': 75, 'height': 100, 'margin-left':'-10px'}   
                )
                
            ])                
        ], width=4),

        dbc.Col([
            dbc.CardGroup([
                dbc.Card([
                    html.Legend('Receita'),
                    html.H5('R$ 10000', id='p-receita-dashboards', style={})        
                ], style = {'padding-left':'20px','padding-top':'10px'}),
                dbc.Card(
                    html.Div(className='fa fa-smile-o', style=card_icon), 
                    color='success',
                    style={'maxwidth': 75, 'height': 100, 'margin-left':'-10px'}   
                )
                
            ])                
        ], width=4),

        dbc.Col([
            dbc.CardGroup([
                dbc.Card([
                    html.Legend('Despesa'),
                    html.H5('R$ 4600', id='p-despesa-dashboards', style={})        
                ], style = {'padding-left':'20px','padding-top':'10px'}),
                dbc.Card(
                    html.Div(className='fa fa-meh-o', style=card_icon), 
                    color='danger',
                    style={'maxwidth': 75, 'height': 100, 'margin-left':'-10px'}   
                )
                
            ])                
        ], width=4)
    ], style={'margin': '10px'}),

    dbc.Row([
        dbc.Col([
            dbc.Card([
                html.Legend("Filtrar lançamentos", className="card-title"),
                html.Label("Categoria das receitas", style = {'margin-top':'10px'}),
                html.Div(
                    dcc.Dropdown(
                        id='dropdown-receita',
                        clearable=False,
                        style={'width': '100%'},
                        persistence=True,
                        persistence_type='session',
                        multi=True)
                ),
                html.Label("Categoria das despesas", style={"margin-top":"10px"}),
                dcc.Dropdown(
                    id='dropdown-despesa',
                    clearable=False,
                    style={"width":"100%"},
                    persistence=True,
                    persistence_type="session",
                    multi=True
                    
                ),
                html.Legend("Período de Análise", style={"margin-top":"10px"}),
                dcc.DatePickerRange(
                    month_format='Do MM, YY',
                    end_date_placeholder_text='Data...',
                    start_date=datetime.today(),
                    end_date=datetime.today() + timedelta(days=31),
                    updatemode='singledate',
                    id='date-picker-config',
                    style={'z-index': '100'}
                ),
                
            ],style={'height':'100%','padding':'20px'})
        ], width=4),

        dbc.Col(
            dbc.Card(
               dcc.Graph(id='graph2'), style={'height':'100%','padding':'10px'} 
            ), width=8
        )
    ], style={'margin':'10px'}),

    dbc.Row([
        dbc.Col(dbc.Card(dcc.Graph(id='graph1'), style={'padding':'10px'}), width=12),
        dbc.Col(dbc.Card(dcc.Graph(id='graph3'), style={'padding':'10px'}), width=6),
        dbc.Col(dbc.Card(dcc.Graph(id='graph4'), style={'padding':'10px'}), width=6),
    ])
       
])



# =========  Callbacks  =========== #

@app.callback(
    [Output("dropdown-receita","options"),
    Output("dropdown-receita","value"),
    Output("p-receita-dashboards", "children")],
    Input("store-receitas", "data")
)
def populate_dropdownvalues(data):
    df = pd.DataFrame(data)
    valor = df['Valor'].sum()
    val = df.Categoria.unique().tolist()


    return ([{"label":x, "value": x} for x in val], val,f"R$ {valor}")

@app.callback(
    [Output("dropdown-despesa","options"),
    Output("dropdown-despesa","value"),
    Output("p-despesa-dashboards", "children")],
    Input("store-despesas", "data")
)
def populate_dropdownvalues(data):
    df = pd.DataFrame(data)
    valor = df['Valor'].sum()
    val = df.Categoria.unique().tolist()


    return ([{"label":x, "value": x} for x in val], val,f"R$ {valor}")


@app.callback(
    Output("p-saldo-dashboards", "children"),
    [Input("store-receitas","data"),
    Input("store-despesas","data")]

)
def saldo_dashboards(receitas, despesas):
    df_receitas = pd.DataFrame(receitas)
    df_despesas = pd.DataFrame(despesas)
    valor = df_receitas['Valor'].sum() - df_despesas['Valor'].sum()
    return f"R$ {valor}"


@app.callback(
    Output('graph1','figure'),

    [Input('store-despesas','data'),
    Input('store-receitas', 'data'),
    Input('dropdown-despesa','value'),
    Input('dropdown-receita','value')]
)
def update_output(data_despesa, data_receita, despesa, receita):
    df_ds = pd.DataFrame(data_despesa).sort_values(by='Data', ascending=True)
    df_rc = pd.DataFrame(data_receita).sort_values(by='Data', ascending=True)

    dfs = [df_ds, df_rc]
    for df in dfs:
        df['Acumulo'] = df['Valor'].cumsum()
        df["Data"] = pd.to_datetime(df["Data"])
        df["Mes"] = df["Data"].apply(lambda x: x.month)

    df_receitas_mes = df_rc.groupby("Mes")["Valor"].sum()
    df_despesas_mes = df_ds.groupby("Mes")["Valor"].sum()
    df_saldo_mes = df_receitas_mes - df_despesas_mes
    df_saldo_mes.to_frame()
    df_saldo_mes = df_saldo_mes.reset_index()
    df_saldo_mes['Acumulado'] = df_saldo_mes['Valor'].cumsum()
    df_saldo_mes['Mes'] = df['Mes'].apply(lambda x: calendar.month_abbr[x])

    df_ds = df_ds[df_ds['Categoria'].isin(despesa)]
    df_rc = df_rc[df_rc['Categoria'].isin(receita)]

    fig = go.Figure()
    
    # fig.add_trace(go.Scatter(name='Despesas', x=df_ds['Data'], y=df_ds['Acumulo'], fill='tonexty', mode='lines'))
    fig.add_trace(go.Scatter(name='Receitas', x=df_rc['Data'], y=df_rc['Acumulo'], fill='tonextx', mode='lines'))
    # fig.add_trace(go.Scatter(name='Saldo Mensal', x=df_saldo_mes['Mes'], y=df_saldo_mes['Acumulado'], mode='lines'))

    fig.update_layout(margin=graph_margin, height=400)
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    return fig

@app.callback(
    Output('graph2', 'figure'),
    [Input('store-receitas', 'data'),
    Input('store-despesas', 'data'),
    Input('dropdown-receita', 'value'),
    Input('dropdown-despesa', 'value'),
    Input('date-picker-config', 'start_date'),
    Input('date-picker-config', 'end_date'), 
    ]
)
def graph2_show(data_receita, data_despesa, receita, despesa, start_date, end_date):
    df_ds = pd.DataFrame(data_despesa)
    df_rc = pd.DataFrame(data_receita)

    dfs = [df_ds, df_rc]

    df_rc['Output'] = 'Receitas'
    df_ds['Output'] = 'Despesas'
    df_final = pd.concat(dfs)

    mask = (df_final['Data'] > start_date) & (df_final['Data'] <= end_date) 
    df_final = df_final.loc[mask]

    df_final = df_final[df_final['Categoria'].isin(receita) | df_final['Categoria'].isin(despesa)]

    fig = px.bar(df_final, x="Data", y="Valor", color='Output', barmode="group")        
    fig.update_layout(margin=graph_margin)
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')

    return fig

@app.callback(
    Output('graph3', "figure"),
    [Input('store-receitas', 'data'),
    Input('dropdown-receita', 'value'),
    ]
)
def pie_receita(data_receita, receita):
    df = pd.DataFrame(data_receita)
    df = df[df['Categoria'].isin(receita)]

    fig = px.pie(df, values=df.Valor, names=df.Categoria, hole=.2)
    fig.update_layout(title={'text': "Receitas"})
    fig.update_layout(margin=graph_margin, height=350, width=350)
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                  
    return fig    

# Gráfico 4
@app.callback(
    Output('graph4', "figure"),
    [Input('store-despesas', 'data'),
    Input('dropdown-despesa', 'value'),
    ]
)
def pie_despesa(data_despesa, despesa):
    df = pd.DataFrame(data_despesa)
    df = df[df['Categoria'].isin(despesa)]

    fig = px.pie(df, values=df.Valor, names=df.Categoria, hole=.2)
    fig.update_layout(title={'text': "Despesas"})

    fig.update_layout(margin=graph_margin ,height=350, width=350)
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')

    return fig






