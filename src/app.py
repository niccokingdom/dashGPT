import dash
import dash_bootstrap_components as dbc
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
from create_summary import create_string
import logging
import os

logger = logging.getLogger("log")

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H5('Select what you would like to explore'),
            dbc.Input(id='input_string', type='text', placeholder='Enter a string'),
        ]),
        dbc.Col([
            html.H5('Select desired number of websites to visit'),
            dbc.Input(id='input_number', type='number', placeholder='Enter a number'),
        ]),
        dbc.Col([
            html.H5('Enter OpenAI API Key to query ChatGPT'),
            dbc.Input(id='open_ai_key', type='text', placeholder='Enter OpenAI API Key'),
        ]),
        dbc.Col([
            dbc.Button('Submit', id='submit_button', n_clicks=0, color='primary')
        ]),
        
    ]),
    html.Br(),
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.Pre(id='output_container', children='Output string will appear here', 
                             style={'width': '100%', 'height': '350px', 'whiteSpace': 'pre-wrap'})
                ]),
            ]),
            dcc.Clipboard(
                target_id='output_container',
                title="copy",
                style={
                    "display": "inline-block",
                    "fontSize": 20,
                    "verticalAlign": "top",
        },
            )
        ]),
    ]),
    html.Br(),
    dbc.Row([
        dbc.Col([
            html.H5('Logging'),
            dcc.Textarea(id='log_area', readOnly=True, style={'width': '100%', 'height': '200px'}),
            dcc.Interval(id='log_interval', interval=1 * 5000),  # Update every second
        ]),
    ]),
])

@app.callback(
    Output('output_container', 'children'),
    Input('submit_button', 'n_clicks'),
    State('input_string', 'value'),
    State('input_number', 'value'),
    State('open_ai_key', 'value'),  # Add the open_ai_key state
    prevent_initial_call=True
)
def update_output(n_clicks, input_string, input_number, open_ai_key):
    if open_ai_key is None or len(open_ai_key) < 10:
        return 'PLEASE INPUT A VALID API KEY'
    else:
        if n_clicks > 0:
            output_string = create_string(input_string, input_number, open_ai_key)
            return output_string
        else:
            return 'Output string will appear here'

@app.callback(
    Output('log_area', 'value'),
    Input('log_interval', 'n_intervals')
)
def update_log_area(n_intervals):
    with open('app.log', 'r') as log_file:
        log_content = log_file.read()
    return log_content

if __name__ == '__main__':
    app.run_server(debug=True, port=8071)#,  host='0.0.0.0')
