"""Layout for upload page"""

from dash import dcc, html

def get_upload_page():
    upload_style = {
        'width': '100%',
        'height': '80px',
        'lineHeight': '80px',
        'borderWidth': '1px',
        'borderStyle': 'dashed',
        'borderRadius': '5px',
        'textAlign': 'center',
        'cursor': 'pointer',
    }
    
    return html.Div([
        html.H4('AY Data'),
        dcc.Upload(
            id='upload-ay',
            children=html.Div(['Drag and drop or ', html.A('select a file')]),
            style=upload_style,
            multiple=False,
        ),
        html.Div(id='ay-filename', style={'margin': '8px 0 20px 0'}),
        html.Div(id='ay-info-box'),

        html.H4('Service Data'),
        dcc.Upload(
            id='upload-service',
            children=html.Div(['Drag and drop or ', html.A('select a file')]),
            style=upload_style,
            multiple=False,
        ),
        html.Div(id='service-filename', style={'margin': '8px 0 20px 0'}),
        html.Div(id='service-info-box'),

        html.Button('Start Dashboard', id='start-btn', n_clicks=0, disabled=True)
    ], style={'maxWidth': '500px', 'margin': '40px auto'})