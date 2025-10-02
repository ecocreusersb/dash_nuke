import dash
from dash import dcc, html, Output, Input
import plotly.express as px
import pandas as pd
import os


def carica_dati_correnti():
    df = pd.read_csv('Nuke_CAP_PCT.csv')
    df["Timestamp"] = pd.to_datetime(df["Timestamp"])
    df = df.set_index("Timestamp")
    df = df.round(0).astype(int)
    df = df.head(500)
    df.index = df.index.strftime('%Y-%m-%d')
    return df


def carica_e_calcola_delta():
    if not (os.path.exists('Nuke_CAP_PCT.csv') and os.path.exists('Nuke_CAP_PCT_LAST.csv')):
        return None
    
    df_new = pd.read_csv('Nuke_CAP_PCT.csv')
    df_old = pd.read_csv('Nuke_CAP_PCT_LAST.csv')

    df_new["Timestamp"] = pd.to_datetime(df_new["Timestamp"])
    df_old["Timestamp"] = pd.to_datetime(df_old["Timestamp"])

    df_new = df_new.set_index("Timestamp").round(0).astype(int)
    df_old = df_old.set_index("Timestamp").round(0).astype(int)

    df_diff = df_new - df_old
    df_diff = df_diff.head(500)
    df_diff.index = df_diff.index.strftime('%Y-%m-%d')

    return df_diff


def crea_figura(dataframe, titolo=""):
    fig = px.imshow(
        dataframe,
        text_auto=True,
        color_continuous_scale='RdYlGn',
        aspect='equal',
        labels=dict(x="Nuclear Plant", y="Data", color=titolo),
        title=titolo
    )

    fig.update_traces(textfont_size=4)

    fig.update_layout(
        width=2000,
        height=3000,
        margin=dict(l=40, r=40, t=80, b=40),
        xaxis_side='top'
    )

    return fig


app = dash.Dash(__name__)
app.title = "Grafico Interattivo Centrali"



app.layout = html.Div(style={
    'padding': '20px',
    'textAlign': 'left'
}, children=[
    html.H1("Nuke Capacity"),

    html.Div(style={'marginBottom': '20px'}, children=[
        html.Button('Mostra Valori Reali', id='btn-reale', n_clicks=0,
                    style={'marginRight': '10px', 'padding': '10px 20px'}),
        html.Button('Mostra Delta', id='btn-delta', n_clicks=0,
                    style={'padding': '10px 20px'}),
    ]),

    dcc.Graph(id='heatmap', figure=crea_figura(carica_dati_correnti()))
])


@app.callback(
    Output('heatmap', 'figure'),
    Input('btn-reale', 'n_clicks'),
    Input('btn-delta', 'n_clicks'),
    prevent_initial_call=True
)
def aggiorna_figura(n_clicks_reale, n_clicks_delta):
    ctx = dash.callback_context

    if not ctx.triggered:
        raise dash.exceptions.PreventUpdate

    button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id == 'btn-reale':
        df = carica_dati_correnti()
        return crea_figura(df, "")
    elif button_id == 'btn-delta':
        df_delta = carica_e_calcola_delta()
        if df_delta is None:
            return px.imshow([[0]], title="⚠️ File CSV mancanti")
        return crea_figura(df_delta, "")
    else:
        raise dash.exceptions.PreventUpdate


if __name__ == '__main__':
    app.run(port=8051, host='0.0.0.0')
