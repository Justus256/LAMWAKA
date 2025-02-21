import dash
import dash_bootstrap_components as dbc
from dash import html, dcc
from dash.dependencies import Input, Output, State
from datetime import datetime, timedelta
import firebase_admin
from firebase_admin import credentials, firestore
import plotly.express as px
import pandas as pd
import os
import json
from dash.dash_table import DataTable

# Initialize Firebase
firebase_credentials = os.getenv('FIREBASE_CONFIG')
if firebase_credentials:
    cred_dict = json.loads(firebase_credentials)
    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred)
    print("Firebase app initialized successfully")
    db = firestore.client()
else:
    print("Firebase credentials not found in environment variables")

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Initialize data lists
inventory_data = []
sales_data = []
debtors_data = []

# Fetch data from Firestore
def fetch_data():
    global db, inventory_data, sales_data, debtors_data
    inventory_data = [doc.to_dict() for doc in db.collection('inventory').stream()]
    sales_data = [doc.to_dict() for doc in db.collection('sales').stream()]
    debtors_data = [doc.to_dict() for doc in db.collection('debtors').stream()]

fetch_data()

app.layout = dbc.Container([
    html.H1('WELCOME TO JUSMEL BEAUTY HAVEN'),
    html.P('Manage your sales, inventory, and debtors efficiently.'),

    # Inventory Management
    dbc.Row([
        dbc.Col(html.Div([
            html.H4('Inventory Management'),
            dbc.Form([
                dbc.Row([
                    dbc.Col(dbc.Input(id='stocked-date', type='date', placeholder='Date Stocked'), width=12, sm=6, md=4, lg=3),
                    dbc.Col(dbc.Input(id='source', type='text', placeholder='Source'), width=12, sm=6, md=4, lg=3),
                    dbc.Col(dbc.Input(id='perfume-name-inventory', type='text', placeholder='Perfume Name'), width=12, sm=6, md=4, lg=3),
                    dbc.Col(dbc.Input(id='amount-paid', type='number', placeholder='Amount Paid'), width=12, sm=6, md=4, lg=3),
                ]),
                dbc.Row([
                    dbc.Col(dbc.Input(id='quantity', type='number', placeholder='Quantity'), width=12, sm=6, md=4, lg=3),
                    dbc.Col(dbc.Select(
                        id='gender',
                        options=[
                            {'label': 'Masculine', 'value': 'Masculine'},
                            {'label': 'Feminine', 'value': 'Feminine'},
                            {'label': 'Unisex', 'value': 'Unisex'}
                        ],
                        placeholder='Gender'
                    ), width=12, sm=6, md=4, lg=3),
                    dbc.Col(dbc.Input(id='description', type='text', placeholder='Description'), width=12, sm=6, md=4, lg=6),
                ]),
                dbc.Row([
                    dbc.Col(dcc.Upload(
                        id='upload-image',
                        children=html.Div(['Drag and Drop or ', html.A('Select a File')]),
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
                    ), width=12, sm=6, md=4, lg=6),
                    dbc.Col(dbc.Input(id='comments', type='text', placeholder='Comments'), width=12, sm=6, md=4, lg=6),
                ]),
                dbc.Button('Add to Inventory', id='add-inventory-btn', color='primary', className='mt-2'),
            ])
        ]), width=12, sm=6, md=4, lg=4),

        # Inventory List as DataTable
        dbc.Col(html.Div([
            html.H5("Inventory List"),
            DataTable(
                id="inventory-data-table",
                columns=[
                    {"name": "Perfume", "id": "perfume_name"},
                    {"name": "Quantity", "id": "quantity"},
                    {"name": "Date Stocked", "id": "stocked_date"},
                    {"name": "Amount Paid", "id": "amount_paid"},
                    {"name": "Gender", "id": "gender"},
                    {"name": "Description", "id": "description"}
                ],
                data=inventory_data,
                style_table={'height': '300px', 'overflowY': 'auto'},
                page_size=10,
                filter_action="native",
                sort_action="native",
            ),
        ]), width=12, sm=6, md=8, lg=8)
    ]),

    # Sales Tracking
    dbc.Row([
        dbc.Col(html.Div([
            html.H4('Sales Tracking'),
            dbc.Form([
                dbc.Row([
                    dbc.Col(dbc.Input(id="sale-date", type='date', placeholder='Date Sold'), width=12, sm=6, md=4, lg=3),
                    dbc.Col(dbc.Input(id='buyer-name', type='text', placeholder='Buyer Name'), width=12, sm=6, md=4, lg=3),
                    dbc.Col(dbc.Input(id='perfume-name-sale', type='text', placeholder='Perfume Name'), width=12, sm=6, md=4, lg=3),
                    dbc.Col(dbc.Input(id='sale-amount', type='number', placeholder='Amount'), width=12, sm=6, md=4, lg=3),
                ]),
                dbc.Row([
                    dbc.Col(dbc.Input(id='sale-comments', type='text', placeholder='Comments'), width=12),
                ]),
                dbc.Button('Record Sale', id='record-sale-btn', color='success', className='mt-2'),
            ])
        ]), width=12, sm=6, md=4, lg=4),

        # Sales List as DataTable
        dbc.Col(html.Div([
            html.H5('Sales List'),
            DataTable(
                id="sales-data-table",
                columns=[
                    {"name": "Buyer", "id": "buyer_name"},
                    {"name": "Perfume", "id": "perfume_name"},
                    {"name": "Date", "id": "sale_date"},
                    {"name": "Amount", "id": "sale_amount"},
                    {"name": "Comments", "id": "sale_comments"}
                ],
                data=sales_data,
                style_table={'height': '300px', 'overflowY': 'auto'},
                page_size=10,
                filter_action="native",
                sort_action="native",
            ),
        ]), width=12, sm=6, md=8, lg=8)
    ]),

    # Debtors Management
    dbc.Row([
        dbc.Col(html.Div([
            html.H4('Debtors Management'),
            dbc.Form([
                dbc.Row([
                    dbc.Col(dbc.Input(id='debtor-name', type='text', placeholder='Debtor Name'), width=12, sm=6, md=4, lg=3),
                    dbc.Col(dbc.Input(id='debtor-phone', type='text', placeholder='Telephone Number'), width=12, sm=6, md=4, lg=3),
                    dbc.Col(dbc.Input(id='debtor-date', type='date', placeholder='Date'), width=12, sm=6, md=4, lg=3),
                    dbc.Col(dbc.Input(id='debtor-amount', type='number', placeholder='Amount'), width=12, sm=6, md=4, lg=3),
                ]),
                dbc.Row([
                    dbc.Col(dbc.Input(id='debtor-comments', type='text', placeholder='Comments'), width=12),
                ]),
                dbc.Button('Add Debtor', id='add-debtor-btn', color='warning', className='mt-2'),
            ])
        ]), width=12, sm=6, md=4, lg=4),

        # Debtors List as DataTable
        dbc.Col(html.Div([
            html.H5('Debtors List'),
            DataTable(
                id="debtors-data-table",
                columns=[
                    {"name": "Debtor", "id": "debtor_name"},
                    {"name": "Phone", "id": "debtor_phone"},
                    {"name": "Date", "id": "debtor_date"},
                    {"name": "Amount", "id": "debtor_amount"},
                    {"name": "Comments", "id": "debtor_comments"}
                ],
                data=debtors_data,
                style_table={'height': '300px', 'overflowY': 'auto'},
                page_size=10,
                filter_action="native",
                sort_action="native",
            ),
        ]), width=12, sm=6, md=8, lg=8)
    ]),

    # Weekly Summary with Date Range Picker
    dbc.Row([
        dbc.Col(html.Div([
            html.H4("Weekly Summaries"),
            dcc.DatePickerRange(
                id='date-range-picker',
                start_date=datetime.now() - timedelta(days=7),
                end_date=datetime.now(),
                display_format='YYYY-MM-DD',
                className='mb-2'
            ),
            dcc.Graph(id="weekly-summary-graph"),
            dbc.Button("Update Summary", id="update-summary-btn", color='info', className='mt-2'),
        ]), width=12)
    ])
], fluid=True)

# Callback Functions for Inventory, Sales, Debtors, and Summary
@app.callback(
    Output("inventory-data-table", "data"),
    Input("add-inventory-btn", 'n_clicks'),
    State("stocked-date", "value"),
    State("source", "value"),
    State("perfume-name-inventory", "value"),
    State("amount-paid", "value"),
    State("quantity", "value"),
    State("gender", "value"),
    State("description", "value"),
    State("upload-image", "contents"),
    State("comments", "value"),
)
def update_inventory_list(n_clicks, stocked_date, source, perfume_name, amount_paid, quantity, gender, description, contents, comments):
    if n_clicks and stocked_date and source and perfume_name and amount_paid and quantity and gender and description:
        inventory_item = {
            'stocked_date': stocked_date,
            'source': source,
            'perfume_name': perfume_name,
            'amount_paid': amount_paid,
            'quantity': quantity,
            'gender': gender,
            'description': description,
            'contents': contents,
            'comments': comments
        }
        db.collection('inventory').add(inventory_item)
        inventory_data.append(inventory_item)
        return inventory_data
    return []

server = app.server
