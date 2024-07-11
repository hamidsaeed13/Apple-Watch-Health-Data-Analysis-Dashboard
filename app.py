import os
import pandas as pd
import dash
import string    
import random
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
from jupyter_dash import JupyterDash
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import base64
from read_apple_watch_data import AppleWatchData
from save_apple_watch_data import *
from flask import session, send_file  
from dash.exceptions import PreventUpdate

# Initialize the Dash app
app = JupyterDash(__name__, external_stylesheets=[
    dbc.themes.MINTY, 
    "https://adminlte.io/themes/v3/dist/css/adminlte.min.css?v=3.2.0"
])
app.config.suppress_callback_exceptions = True
app.server.secret_key = os.urandom(24)

# Set default start date to '2005-01-01'
default_start_date = datetime(2005, 1, 1).date()
# Get current date and time
current_datetime = datetime.now()
# Set default end date and time (1 day ahead)
default_end_date = (current_datetime + timedelta(days=1)).date()

# Initialize processing variable
processing = False
# Define the content of the about section
about_content = dbc.Card(
    dbc.CardBody(
        [
            html.P("Welcome to the Apple Watch XML Analyzer!"),
            html.P(
                "This free tool is designed to analyze exported XML files from Apple Watch, "
                "making it accessible to patients, doctors, and researchers alike. It provides "
                "the capability to convert XML data into CSV format for easier processing and analysis."
            ),
            html.P(html.Strong("Contact Information:")),
            html.Ul(
                [
                    html.Li(html.A("Email: hamid@iub.edu.pk", href="mailto:hamid@iub.edu.pk")),
                    html.Li(html.A("Phone: +923012216201", href="tel:+923012216201")),
                ]
            ),
            html.P(
                "Feel free to reach out to us if you encounter any issues or have suggestions "
                "for new features. Your feedback helps us improve the app for everyone!"
            ),
        ]
    ),
    className="card",
)
# Assuming this is within your Dash app layout setup
download_links = dbc.Card(
    className="download-card",
    children=[
        dbc.CardBody(
            className="card-body",
            children=[
                html.H3("Download CSV Files", className="card-title"),
                dbc.Row([
                    dbc.Col(
                        dbc.Card(
                            className="download-link-card",
                            children=[
                                dbc.CardBody(
                                    children=[
                                        html.A('Heart Rate', href='/download/heart_rate.csv', target='_blank', className='download-link'),
                                    ]
                                )
                            ]
                        )
                    ),
                    dbc.Col(
                        dbc.Card(
                            className="download-link-card",
                            children=[
                                dbc.CardBody(
                                    children=[
                                        html.A('Heart Rate Variability', href='/download/heart_rate_variability.csv', target='_blank', className='download-link'),
                                    ]
                                )
                            ]
                        )
                    ),
                    dbc.Col(
                        dbc.Card(
                            className="download-link-card",
                            children=[
                                dbc.CardBody(
                                    children=[
                                        html.A('Resting Heart Rate', href='/download/resting_heart_rate.csv', target='_blank', className='download-link'),
                                    ]
                                )
                            ]
                        )
                    ),
                    dbc.Col(
                        dbc.Card(
                            className="download-link-card",
                            children=[
                                dbc.CardBody(
                                    children=[
                                        html.A('Walking Heart Rate', href='/download/walking_heart_rate.csv', target='_blank', className='download-link'),
                                    ]
                                )
                            ]
                        )
                    ),
                    dbc.Col(
                        dbc.Card(
                            className="download-link-card",
                            children=[
                                dbc.CardBody(
                                    children=[
                                        html.A('Distance Walked', href='/download/distance_walked_ran.csv', target='_blank', className='download-link'),
                                    ]
                                )
                            ]
                        )
                    ),
                    dbc.Col(
                        dbc.Card(
                            className="download-link-card",
                            children=[
                                dbc.CardBody(
                                    children=[
                                        html.A('Basal Energy', href='/download/basal_energy.csv', target='_blank', className='download-link'),
                                    ]
                                )
                            ]
                        )
                    ),
                    dbc.Col(
                        dbc.Card(
                            className="download-link-card",
                            children=[
                                dbc.CardBody(
                                    children=[
                                        html.A('Stand Hours', href='/download/stand_hour.csv', target='_blank', className='download-link'),
                                    ]
                                )
                            ]
                        )
                    ),
                    dbc.Col(
                        dbc.Card(
                            className="download-link-card",
                            children=[
                                dbc.CardBody(
                                    children=[
                                        html.A('Steps Count', href='/download/step_counts.csv', target='_blank', className='download-link'),
                                    ]
                                )
                            ]
                        )
                    )
                ])
            ]
        )
    ]
)

# Define the layout
app.layout = dbc.Container([
    html.Div([
        html.Img(src="/assets/logo.png", height="60px"),  # Add your image file path here
        html.H2("Apple Watch Health Data Analysis Dashboard", style={"margin-left": "10px", "display": "inline-block"})
    ]),
    html.Hr(),
    html.Div([
        html.H3("Import File"),
        dcc.Upload(
            id='upload-data',
            children=html.Div([
                'Drag and Drop or ',
                html.A('Select XML File')
            ]),
            style={
                'width': '100%',
                'height': '60px',
                'lineHeight': '60px',
                'borderWidth': '1px',
                'borderStyle': 'dashed',
                'borderRadius': '5px',
                'textAlign': 'center',
                'margin': '10px'
            },
            multiple=False
        ),
        dbc.Progress(id="progress", value=0),
        html.Div([
            html.Button('Upload File', id='upload-button', n_clicks=0, style={'margin-right': '10px'}),
            html.Button('Download CSV', id='download-csv-button', n_clicks=0, style={'background-color': 'green', 'color': 'white'}),
        ], style={'display': 'flex', 'justify-content': 'space-between'}),
        html.Div(id='output-data-upload'),
    ]),
    dbc.Tabs([
        dbc.Tab(label="Import File", tab_id="import-file"),
        dbc.Tab(label="Graphs", tab_id="graphs"),
        dbc.Tab(label="About", tab_id="about"),
    ], id="tabs", active_tab="import-file"),
    html.Div(id="tab-content"),
    dcc.Interval(id='progress-interval', interval=100, n_intervals=0),
    html.Div(id='output-Personal-info', style={'display': 'none'}),  # Hidden div to store personal info output
])

# Callback to handle tab content rendering
@app.callback(
    Output("tab-content", "children"),
    [Input("tabs", "active_tab")]
)
def render_tab_content(active_tab):
    if active_tab == "import-file":
        data=session.get('personal_data',[])
        if not data:
            return html.Div([
                html.H3("Personal Information"),
                html.Div(id='output-Personal-info'),
                html.Hr()])
        personal_info = html.Div([
            html.Div(className="card card-primary card-outline", children=[
                html.Div(className="card-body box-profile", children=[
                    html.H3(className="profile-username text-center", children=data[0].get("UserName", "N/A")),
                    html.P(className="text-muted text-center", children="User Profile"),
                    html.Ul(className="list-group list-group-unbordered mb-3", children=[
                        html.Li(className="list-group-item", children=[
                            html.B("Date of Birth"), html.A(className="float-right", children=data[0].get("DateOfBirth", "N/A"))
                        ]),
                        html.Li(className="list-group-item", children=[
                            html.B("Biological Sex"), html.A(className="float-right", children=data[0].get("BiologicalSex", "N/A"))
                        ]),
                        html.Li(className="list-group-item", children=[
                            html.B("Blood Type"), html.A(className="float-right", children=data[0].get("BloodType", "N/A"))
                        ]),
                        html.Li(className="list-group-item", children=[
                            html.B("Fitzpatrick Skin Type"), html.A(className="float-right", children=data[0].get("FitzpatrickSkinType", "N/A"))
                        ]),
                        html.Li(className="list-group-item", children=[
                            html.B("Cardio Fitness Medications Use"), html.A(className="float-right", children=data[0].get("CardioFitnessMedicationsUse", "N/A"))
                        ]),
                        html.Li(className="list-group-item", children=[
                            html.B("Height"), html.A(className="float-right", children=data[1].get("value", "N/A") +" "+ data[1].get("unit", "N/A"))
                        ])
                        ,
                        html.Li(className="list-group-item", children=[
                            html.B("Body Mass"), html.A(className="float-right", children=data[2].get("value", "N/A") +" " + data[2].get("unit", "N/A"))
                        ])
                    ]),
                    html.A(href="#", className="btn btn-primary btn-block", children=html.B("More Details"))
                ])
            ])
        ])
        return html.Div([html.H3("Personal Information"),
            html.Div(id='output-Personal-info', children=personal_info),
            html.Hr()])
    elif active_tab == "graphs":
        return html.Div([
            html.H3("Graphs"),
            dbc.Row([
                dbc.Col([
                    dcc.DatePickerRange(
                        id='date-picker-range',
                        start_date_placeholder_text='Start Date',
                        end_date_placeholder_text='End Date',
                        calendar_orientation='vertical',
                        display_format='YYYY-MM-DD',
                        start_date=default_start_date,
                        end_date=default_end_date,
                        style={'width': '100%'}
                    ),
                    dcc.Input(
                        id='start-time',
                        type='text',
                        placeholder='Start Time (HH:MM)',
                        value='00:00',
                        style={'margin': '10px'}
                    ),
                    dcc.Input(
                        id='end-time',
                        type='text',
                        placeholder='End Time (HH:MM)',
                        value='23:59',
                        style={'margin': '10px'}
                    ),
                    html.Button('Generate Graphs', id='generate-graphs-button', n_clicks=0, style={'margin': '10px'}),
                    html.Hr()
                ], md=4),
                dbc.Col([
                    html.Div(id='output-graphs'),
                    html.Hr()
                ], md=8)
            ])
        ])
    elif active_tab == "about":
        return html.Div(
                        className="container-fluid",
                        children=[
                            # About section card
                            about_content,
                        ])

# Callback to update the upload text when a file is selected
@app.callback(
    Output('upload-data', 'children'),
    [Input('upload-data', 'filename')]
)
def update_upload_text(filename):
    if filename:
        return html.Div([f"File {filename} selected. Please click the upload button."])
    else:
        return html.Div([
            'Drag and Drop or ',
            html.A('Select XML File')
        ])

# Callback to handle file upload
@app.callback(
    [Output('output-data-upload', 'children'), Output('progress', 'value'), Output('output-Personal-info', 'children')],
    [Input('upload-button', 'n_clicks')],
    [State('upload-data', 'filename'),
     State('upload-data', 'contents')]
)
def update_output(n_clicks, filename, contents):
    if n_clicks > 0:
        if filename is None or contents is None:
            raise PreventUpdate

        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        S = 10  # number of characters in the string.  
        # call random.choices() string module to find the string in Uppercase + numeric data.  
        ran = ''.join(random.choices(string.ascii_uppercase + string.digits, k = S))   
        file_path = f"{ran}_{filename}"
        with open(file_path, 'wb') as f:
            f.write(decoded)

        # Save file path in session
        session['xml_data_file_path'] = file_path
        apple_watch = AppleWatchData(file_path, 'A’s Apple Watch')
        data=apple_watch.load_Personal_data()
        session['personal_data']=data
        
        personal_info = html.Div([
            html.Div(className="card card-primary card-outline", children=[
                html.Div(className="card-body box-profile", children=[
                    html.H3(className="profile-username text-center", children=data[0].get("UserName", "N/A")),
                    html.P(className="text-muted text-center", children="User Profile"),
                    html.Ul(className="list-group list-group-unbordered mb-3", children=[
                        html.Li(className="list-group-item", children=[
                            html.B("Date of Birth"), html.A(className="float-right", children=data[0].get("DateOfBirth", "N/A"))
                        ]),
                        html.Li(className="list-group-item", children=[
                            html.B("Biological Sex"), html.A(className="float-right", children=data[0].get("BiologicalSex", "N/A"))
                        ]),
                        html.Li(className="list-group-item", children=[
                            html.B("Blood Type"), html.A(className="float-right", children=data[0].get("BloodType", "N/A"))
                        ]),
                        html.Li(className="list-group-item", children=[
                            html.B("Fitzpatrick Skin Type"), html.A(className="float-right", children=data[0].get("FitzpatrickSkinType", "N/A"))
                        ]),
                        html.Li(className="list-group-item", children=[
                            html.B("Cardio Fitness Medications Use"), html.A(className="float-right", children=data[0].get("CardioFitnessMedicationsUse", "N/A"))
                        ]),
                        html.Li(className="list-group-item", children=[
                            html.B("Height"), html.A(className="float-right", children=data[1].get("value", "N/A") +" "+ data[1].get("unit", "N/A"))
                        ])
                        ,
                        html.Li(className="list-group-item", children=[
                            html.B("Body Mass"), html.A(className="float-right", children=data[2].get("value", "N/A") +" " + data[2].get("unit", "N/A"))
                        ])
                    ]),
                    html.A(href="#", className="btn btn-primary btn-block", children=html.B("More Details"))
                ])
            ])
        ])
        
        
        return html.Div([
            html.P(f"Uploaded file: {filename}"),
        ]), 100,personal_info
    else:
        raise PreventUpdate

# Callback to generate graphs based on selected dates
@app.callback(
    Output('output-graphs', 'children'),
    [Input('generate-graphs-button', 'n_clicks')],
    [State('date-picker-range', 'start_date'),
     State('date-picker-range', 'end_date'),
     State('start-time', 'value'),
     State('end-time', 'value')]
)
def generate_graphs(n_clicks, start_date, end_date, start_time, end_time):
    global processing

    if n_clicks > 0 and not processing:
        processing = True

        # Get file path from session
        xml_data_file_path = session.get('xml_data_file_path', '')

        if not xml_data_file_path:
            processing = False
            return html.Div([
                dbc.Progress(id="progress", value=0, animated=True),
                html.Div("No file Uploaded.")
            ])

        source_name = 'A’s Apple Watch'

        try:
            START_DATE = datetime.strptime(f"{start_date} {start_time}", '%Y-%m-%d %H:%M')
            END_DATE = datetime.strptime(f"{end_date} {end_time}", '%Y-%m-%d %H:%M')
        except ValueError:
            START_DATE = datetime.strptime(start_date, '%Y-%m-%d')
            END_DATE = datetime.strptime(end_date, '%Y-%m-%d')

        apple_watch = AppleWatchData(xml_data_file_path, source_name)
        
        # Initialize list to store figures
        figures = []

        # Heart Rate Variability Data
        df = apple_watch.load_heart_rate_variability_data()
        df = df[(df['start_timestamp'] > START_DATE) & (df['start_timestamp'] < END_DATE)]
        if not df.empty:
            df['date'] = df['start_timestamp'].dt.strftime('%Y-%m-%d')
            df['time'] = df['start_timestamp'].dt.strftime('%H:%M:%S')
            fig = px.scatter(df, x='date', y='heart_rate_variability', color='date',
                             title='Apple Watch Heart Rate Variability (SDNN)',
                             labels={'date': 'Date', 'heart_rate_variability': 'Time Between Heart Beats (ms)'},
                             hover_data={'date': True, 'time': True, 'heart_rate_variability': True})
            fig.update_layout(
                width=800,
                height=600,
                xaxis={'title': {'text': 'Date'}, 'tickangle': 45},
                yaxis={'title': {'text': 'Time Between Heart Beats (ms)'}},
                hoverlabel={'namelength': -1},
                title={'x': 0.5, 'y': 0.9, 'xanchor': 'center', 'yanchor': 'top', 'font': {'size': 16}}
            )
            figures.append(html.Div([
                html.H3("Apple Watch Heart Rate Variability (SDNN)"),
                dcc.Graph(figure=fig)
            ]))
            figures.append(html.Hr())

        # Heart Rate Data
        df = apple_watch.load_heart_rate_data()
        df = df[(df['start_timestamp'] > START_DATE) & (df['start_timestamp'] < END_DATE)]
        if not df.empty:
            df['date'] = df['start_timestamp'].dt.strftime('%m/%d/%y')
            df['time'] = df['start_timestamp'].dt.time
            fig2 = make_subplots(rows=1, cols=1)
            color_palette = px.colors.qualitative.T10
            dates = df['date'].unique()
            for idx, dt in enumerate(dates):
                sub_df = df[df['date'] == dt]
                fig2.add_trace(go.Scatter(
                    x=sub_df['time'],
                    y=sub_df['heart_rate'],
                    mode='markers',
                    marker=dict(color=color_palette[idx % len(color_palette)]),
                    name=dt,
                    text=[f"Date: {d}, Time: {t}, BPM: {bpm}" for d, t, bpm in zip(sub_df['date'], sub_df['start_timestamp'], sub_df['heart_rate'])]
                ))
            fig2.update_layout(
                width=800,
                height=600,
                title='Apple Watch Heart Rate Data',
                xaxis_title='Hour',
                yaxis_title='Average Beats Per Minute',
                hovermode='closest'
            )
            figures.append(html.Div([
                html.H3("Apple Watch Heart Rate Data"),
                dcc.Graph(figure=fig2)
            ]))
            figures.append(html.Hr())

        # Resting Heart Rate Data
        df = apple_watch.load_resting_heart_rate_data()
        df = df[(df['start_timestamp'] > START_DATE) & (df['start_timestamp'] < END_DATE)]
        if not df.empty:
            df['date'] = df['start_timestamp'].dt.strftime('%m/%d/%y')
            fig3 = px.bar(
                df, x='start_timestamp', y='resting_heart_rate',
                title='Apple Watch Resting Heart Rate',
                labels={'start_timestamp': 'Date', 'resting_heart_rate': 'Average Beats Per Minute'},
                hover_data=['date']
            )
            fig3.update_layout(
                width=800,
                height=600,
                xaxis_title='Date',
                yaxis_title='Average Beats Per Minute',
                hovermode='closest'
            )
            figures.append(html.Div([
                html.H3("Apple Watch Resting Heart Rate"),
                dcc.Graph(figure=fig3)
            ]))
            figures.append(html.Hr())

        # Walking Heart Rate Data
        try:
            df = apple_watch.load_walking_heart_rate_data()
            df = df[(df['start_timestamp'] > START_DATE) & (df['start_timestamp'] < END_DATE)]
            if not df.empty:
                df['date'] = df['start_timestamp'].dt.strftime('%m/%d/%y')
                fig4 = px.line(
                    df, x='start_timestamp', y='walking_heart_rate',
                    title='Apple Watch Walking Heart Rate',
                    labels={'start_timestamp': 'Date', 'walking_heart_rate': 'Average Beats Per Minute'},
                    hover_data=['date']
                )
                fig4.update_layout(
                    width=800,
                    height=600,
                    xaxis_title='Date',
                    yaxis_title='Average Beats Per Minute',
                    hovermode='closest'
                )
                figures.append(html.Div([
                    html.H3("Apple Watch Walking Heart Rate"),
                    dcc.Graph(figure=fig4)
                ]))
                figures.append(html.Hr())
        except (IndexError, ValueError):
            logger.warning('Missing walking heart rate data!')

        # Hourly Distance Walked/Ran Data
        try:
            df = apple_watch.load_distance_data()
            df = df[(df['start_timestamp'] > START_DATE) & (df['start_timestamp'] < END_DATE)]
            if not df.empty:
                df['date'] = df['start_timestamp'].dt.strftime('%m/%d/%y')
                df['hour'] = df['start_timestamp'].dt.hour
                hourly_distance = df.groupby(['hour', 'date'])['distance_walk_run'].sum().reset_index()
                hourly_distance['datetime'] = pd.to_datetime(hourly_distance['date'])
                hourly_distance.sort_values(by=['datetime'], inplace=True)
                fig5 = px.density_heatmap(
                    hourly_distance, x='hour', y='date', z='distance_walk_run',
                    title='Apple Watch Hourly Distance Walked/Ran',
                    labels={'hour': 'Hour', 'date': 'Date', 'distance_walk_run': 'Miles'},
                    color_continuous_scale='Viridis'
                )
                fig5.update_layout(
                    width=800,
                    height=600,
                    xaxis_nticks=24,
                    yaxis={'categoryorder': 'category ascending'},
                    hovermode='closest'
                )
                figures.append(html.Div([
                    html.H3("Apple Watch Hourly Distance Walked/Ran"),
                    dcc.Graph(figure=fig5)
                ]))
                figures.append(html.Hr())
        except (IndexError, ValueError):
            logger.warning('Missing hourly distance walked/ran data!')

        # Hourly Basal Energy Data
        try:
            df = apple_watch.load_basal_energy_data()
            df = df[(df['start_timestamp'] > START_DATE) & (df['start_timestamp'] < END_DATE)]
            if not df.empty:
                df['date'] = df['start_timestamp'].dt.strftime('%m/%d/%y')
                df['hour'] = df['start_timestamp'].dt.hour
                basal_energy = df.groupby(['hour', 'date'])['energy_burned'].sum().reset_index()
                basal_energy['datetime'] = pd.to_datetime(basal_energy['date'])
                basal_energy.sort_values(by=['datetime'], inplace=True)
                fig6 = px.density_heatmap(
                    basal_energy, x='hour', y='date', z='energy_burned',
                    title='Apple Watch Hourly Calories Burned',
                    labels={'hour': 'Hour', 'date': 'Date', 'energy_burned': 'Calories'},
                    color_continuous_scale='Viridis'
                )
                fig6.update_layout(
                    width=800,
                    height=600,
                    xaxis_nticks=24,
                    yaxis={'categoryorder': 'category ascending'},
                    hovermode='closest'
                )
                figures.append(html.Div([
                    html.H3("Apple Watch Hourly Calories Burned"),
                    dcc.Graph(figure=fig6)
                ]))
                figures.append(html.Hr())
        except (IndexError, ValueError):
            logger.warning('Missing hourly calories burned data!')

        # Hourly Stand Hours Data
        try:
            df = apple_watch.load_stand_hour_data()
            df = df[(df['start_timestamp'] > START_DATE) & (df['start_timestamp'] < END_DATE)]
            if not df.empty:
                df['date'] = df['start_timestamp'].dt.strftime('%m/%d/%y')
                df['hour'] = df['start_timestamp'].dt.hour
                df['stand_hour'] = list(map(lambda label: 1 if label == 'Stood' else 0, df['stand_hour']))
                stand_hours = df.groupby(['hour', 'date'])['stand_hour'].sum().reset_index()

                stand_hours['datetime'] = pd.to_datetime(stand_hours['date'])
                stand_hours.sort_values(by=['datetime'], inplace=True)
                fig7 = px.density_heatmap(
                    stand_hours, x='hour', y='date', z='stand_hour',
                    title='Apple Watch Hourly Stand Hours',
                    labels={'hour': 'Hour', 'date': 'Date', 'stand_hour': 'Standing Hours'},
                    color_continuous_scale='Viridis'
                )
                fig7.update_layout(
                    width=800,
                    height=600,
                    xaxis_nticks=24,
                    yaxis={'categoryorder': 'category ascending'},
                    hovermode='closest'
                )
                figures.append(html.Div([
                    html.H3("Apple Watch Hourly Stand Hours"),
                    dcc.Graph(figure=fig7)
                ]))
                figures.append(html.Hr())
        except (IndexError, ValueError):
            logger.warning('Missing hourly stand hours data!')
        try:
            df = apple_watch.load_step_data()
            df = df[(df['start_timestamp'] > START_DATE) & (df['start_timestamp'] < END_DATE)]
            df['date'] = df['start_timestamp'].dt.strftime('%m/%d/%y')
            df['hour'] = df['start_timestamp'].dt.hour
        
            # Group by hour and date and calculate sum of steps
            step_counts = df.groupby(['hour', 'date'])['steps'].sum().reset_index()
        
            # Create a grid heatmap of hourly counts grouped by date
            fig8 = go.Figure(data=go.Heatmap(
                z=step_counts['steps'],
                x=step_counts['hour'],
                y=step_counts['date'],
                colorscale='Viridis',
                hoverongaps = False
            ))
        
            fig8.update_layout(
                title='Apple Watch Hourly Step Counts',
                xaxis_title='Hour',
                yaxis_title='Date',
                xaxis={'tickvals': list(range(24))},
                yaxis={'categoryorder': 'category ascending'},
                width=800,
                height=600,
                font=dict(
                    size=12
                )
            )
            figures.append(html.Div([
                        html.H3("Apple Watch Hourly Step Counts"),
                        dcc.Graph(figure=fig8)
                    ]))
            figures.append(html.Hr())
        except (IndexError, ValueError):
            logger.warning('Missing Hourly Step Counts data!')

        processing = False
        return html.Div([
            html.H3("Generated Graphs"),
            *figures
        ])
    else:
        if not session.get('xml_data_file_path'):
            return html.Div([
                dbc.Progress(id="progress", value=0, animated=True),
                html.Div("No file Uploaded.")
            ])
        return html.Div([
            dbc.Progress(id="progress", value=100, animated=True),
            html.Div("Click to Generate graphs...")
        ])


# Callback to handle CSV download
@app.callback(
    Output('output-data-upload', 'children', allow_duplicate=True),
    [Input('download-csv-button', 'n_clicks')],
    prevent_initial_call=True
)
def download_csv(n_clicks):
    if n_clicks > 0:
        # Get file path from session
        xml_data_file_path = session.get('xml_data_file_path', '')

        if not xml_data_file_path:
            return html.Div([
                html.P("No file uploaded.")
            ])

        source_name = 'A’s Apple Watch'
        apple_watch = AppleWatchData(xml_data_file_path, source_name)
        tocsv(apple_watch)
        
        try:
            return download_links
        except Exception as e:
            return html.Div([
                html.P(f"Error generating CSV: {str(e)}")
            ])
# Flask route to serve the CSV file
@app.server.route('/download/<path:filename>')
def download_file(filename):
    try:
        # Construct the full path to the file within the 'download' folder
        file_path = f"./download/{filename}"
        
        # Use send_file to send the file as an attachment
        return send_file(file_path, as_attachment=True)
    except Exception as e:
        return str(e), 404

app.css.append_css({
    'external_url': 'https://stackpath.bootstrapcdn.com/bootstrap/4.5.0/css/bootstrap.min.css'
})
# Run the app
if __name__ == "__main__":
    app.run_server(debug=False)
