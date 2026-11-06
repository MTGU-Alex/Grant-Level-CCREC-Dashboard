from dash import html, dcc


def _upload_card(step, title, key):
    """key is 'ay' or 'service' – matches your existing component ids."""
    return html.Div([
        html.Div([
            html.Span(step, className='step-badge'),
            html.H4(title),
        ], className='upload-card-header'),

        dcc.Upload(
            id=f'upload-{key}',
            children=html.Div([
                html.Div('📄', className='upload-zone-icon'),
                html.Div(['Drag and drop or ', html.A('select a file')],
                         className='upload-zone-text'),
                html.Div('CSV or Excel', className='upload-zone-hint'),  # edit to suit
            ]),
            className='upload-zone',
            className_active='upload-zone--active',
            multiple=False,
        ),

        # Spinner shows whenever the callback that updates these children is running
        dcc.Loading(
            type='circle',
            color='#4f46e5',
            children=html.Div([
                html.Div(id=f'{key}-filename', className='filename'),
                html.Div(id=f'{key}-info-box'),
            ], className='status-area'),
        ),

        dcc.Store(id=f'{key}-valid', data=False),
    ], className='upload-card')


def get_upload_page():
    return html.Div([
        html.H2('Upload your data'),
        html.P('Upload both files to get started.', className='upload-subtitle'),

        _upload_card('1', 'AY Data', 'ay'),
        _upload_card('2', 'Service Data', 'service'),

        html.Button('Start Dashboard', id='start-btn', n_clicks=0,
                    disabled=True, className='start-btn'),
    ], className='upload-page')