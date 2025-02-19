import dash
import dash_bootstrap_components as dbc
from dash import html, dcc
from dash.dependencies import Input, Output, State
from datetime import datetime, timedelta
import base64
import io
import firebase_admin
from firebase_admin import credentials, firestore
import plotly.express as px
import pandas as pd
import os
import json

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
    global inventory_data, sales_data, debtors_data
    inventory_data = [doc.to_dict() for doc in db.collection('inventory').stream()]
    sales_data = [doc.to_dict() for doc in db.collection('sales').stream()]
    debtors_data = [doc.to_dict() for doc in db.collection('debtors').stream()]

fetch_data()

app.layout = dbc.Container([
    html.H1('WELCOME TO JUSMEL BEAUTY HAVEN'),
    html.P('Manage your sales, inventory, and debtors efficiently.'),

    dbc.Row([
        dbc.Col(html.Div([
            html.H4('Inventory Management'),
            html.P("Date stocked, source, perfume name, amount paid, quantity, gender, description, image, comments."),
            dbc.Form([
                dbc.Row([
                    dbc.Col(dbc.Input(id='stocked-date', type='date', placeholder='Date Stocked'), width=6, sm=12, lg=3),
                    dbc.Col(dbc.Input(id='source', type='text', placeholder='Source'), width=6, sm=12, lg=3),
                    dbc.Col(dbc.Input(id='perfume-name-inventory', type='text', placeholder='Perfume Name'), width=6, sm=12, lg=3),
                    dbc.Col(dbc.Input(id='amount-paid', type='number', placeholder='Amount Paid'), width=6, sm=12, lg=3),
                ]),
                dbc.Row([
                    dbc.Col(dbc.Input(id='quantity', type='number', placeholder='Quantity'), width=6, sm=12, lg=3),
                    dbc.Col(dbc.Select(
                        id='gender',
                        options=[
                            {'label': 'Masculine', 'value': 'Masculine'},
                            {'label': 'Feminine', 'value': 'Feminine'},
                            {'label': 'Unisex', 'value': 'Unisex'}
                        ],
                        placeholder='Gender'
                    ), width=6, sm=12, lg=3),
                    dbc.Col(dbc.Input(id='description', type='text', placeholder='Description'), width=12, lg=6),
                ]),
                dbc.Row([
                    dbc.Col(dcc.Upload(
                        id='upload-image',
                        children=html.Div([
                            'Drag and Drop or ',
                            html.A('Select a File')
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
                    ), width=12, lg=6),
                    dbc.Col(dbc.Input(id='comments', type='text', placeholder='Comments'), width=12, lg=6),
                ]),
                dbc.Button('Add to Inventory', id='add-inventory-btn', color='primary', className='mt-2'),
            ])
        ]), width=12, lg=4),

        dbc.Col(html.Div([
            html.H5("Inventory List"),
            html.Div(id='inventory-list', children=[
                html.Li(f"Perfume: {item['perfume_name']}, Quantity: {item['quantity']}, Date: {item['stocked_date']}, Amount Paid: {item['amount_paid']}.") for item in inventory_data
            ]),
        ]), width=12, lg=8)
    ]),

    dbc.Row([
        dbc.Col(html.Div([
            html.H4('Sales Tracking'),
            html.P('Date sold, buyer name, perfume name, amount, comments.'),
            dbc.Form([
                dbc.Row([
                    dbc.Col(dbc.Input(id="sale-date", type='date', placeholder='Date Sold'), width=6, sm=12, lg=3),
                    dbc.Col(dbc.Input(id='buyer-name', type='text', placeholder='Buyer Name'), width=6, sm=12, lg=3),
                    dbc.Col(dbc.Input(id='perfume-name-sale', type='text', placeholder='Perfume Name'), width=6, sm=12, lg=3),
                    dbc.Col(dbc.Input(id='sale-amount', type='number', placeholder='Amount'), width=6, sm=12, lg=3),
                ]),
                dbc.Row([
                    dbc.Col(dbc.Input(id='sale-comments', type='text', placeholder='Comments'), width=12),
                ]),
                dbc.Button('Record Sale', id='record-sale-btn', color='success', className='mt-2'),
            ])
        ]), width=12, lg=4),

        dbc.Col(html.Div([
            html.H5('Sales List'),
            html.Ul(id="sales-list", children=[
                html.Li(f"Buyer: {item['buyer_name']}, Perfume: {item['perfume_name']}, Date: {item['sale_date']}, Amount: {item['sale_amount']}. Comments: {item['sale_comments']}") for item in sales_data
            ]),
        ]), width=12, lg=8)
    ]),
    dbc.Row([
        dbc.Col(html.Div([
            html.H4('Debtors Management'),
            html.P('Debtor name, telephone number, date, amount, comments.'),
            dbc.Form([
                dbc.Row([
                    dbc.Col(dbc.Input(id='debtor-name', type='text', placeholder='Debtor Name'), width=6, sm=12, lg=3),
                    dbc.Col(dbc.Input(id='debtor-phone', type='text', placeholder='Telephone Number'), width=6, sm=12, lg=3),
                    dbc.Col(dbc.Input(id='debtor-date', type='date', placeholder='Date'), width=6, sm=12, lg=3),
                    dbc.Col(dbc.Input(id='debtor-amount', type='number', placeholder='Amount'), width=6, sm=12, lg=3),
                ]),
                dbc.Row([
                    dbc.Col(dbc.Input(id='debtor-comments', type='text', placeholder='Comments'), width=12),
                ]),
                dbc.Button('Add Debtor', id='add-debtor-btn', color='warning', className='mt-2'),
            ])
        ]), width=12, lg=4),

        dbc.Col(html.Div([
            html.H5('Debtors List'),
            html.Ul(id="debtors-list", children=[
                html.Li(f"Debtor: {item['debtor_name']}, Phone: {item['debtor_phone']}, Date: {item['debtor_date']}, Amount: {item['debtor_amount']}. Comments: {item['debtor_comments']}") for item in debtors_data
            ]),
        ]), width=12, lg=8)
    ]),

    dbc.Row([
        dbc.Col(html.Div([
            html.H4("Weekly Summaries"),
            dcc.Graph(id="weekly-summary-graph"),
            dbc.Button("Update Summary", id="update-summary-btn", color='info', className='mt-2'),
        ]), width=12)
    ])
], fluid=True)

@app.callback(
    Output("inventory-list", "children"),
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
        return [html.Li(f"Perfume: {item['perfume_name']}, Quantity: {item['quantity']}, Date: {item['stocked_date']}, Amount Paid: {item['amount_paid']}.") for item in inventory_data]
        db.collection('inventory').add(inventory_item)
        inventory_data.append(inventory_item)
        return [html.Li(f"Perfume: {item['perfume_name']}, Quantity: {item['quantity']}, Date: {item['stocked_date']}, Amount Paid: {item['amount_paid']}.") for item in inventory_data]
    return []

@app.callback(
    Output("sales-list", "children"),
    Input("record-sale-btn", 'n_clicks'),
    State("sale-date", "value"),
    State("buyer-name", "value"),
    State("perfume-name-sale", "value"),
    State("sale-amount", "value"),
    State("sale-comments", "value"),
)
def update_sales_list(n_clicks, sale_date, buyer_name, perfume_name, sale_amount, sale_comments):
    if n_clicks and sale_date and buyer_name and perfume_name and sale_amount:
        sale_item = {
            'sale_date': sale_date,
            'buyer_name': buyer_name,
            'perfume_name': perfume_name,
            'sale_amount': sale_amount,
            'sale_comments': sale_comments
        }
        db.collection('sales').add(sale_item)
        sales_data.append(sale_item)
        return [html.Li(f"Buyer: {item['buyer_name']}, Perfume: {item['perfume_name']}, Date: {item['sale_date']}, Amount: {item['sale_amount']}. Comments: {item['sale_comments']}") for item in sales_data]
    return []

@app.callback(
    Output("debtors-list", "children"),
    Input("add-debtor-btn", 'n_clicks'),
    State("debtor-name", "value"),
    State("debtor-phone", "value"),
    State("debtor-date", "value"),
    State("debtor-amount", "value"),
    State("debtor-comments", "value"),
)
def update_debtors_list(n_clicks, debtor_name, debtor_phone, debtor_date, debtor_amount, debtor_comments):
    if n_clicks and debtor_name and debtor_phone and debtor_date and debtor_amount:
        debtor_item = {
            'debtor_name': debtor_name,
            'debtor_phone': debtor_phone,
            'debtor_date': debtor_date,
            'debtor_amount': debtor_amount,
            'debtor_comments': debtor_comments
        }
        db.collection('debtors').add(debtor_item)
        debtors_data.append(debtor_item)
        return [html.Li(f"Debtor: {item['debtor_name']}, Phone: {item['debtor_phone']}, Date: {item['debtor_date']}, Amount: {item['debtor_amount']}. Comments: {item['debtor_comments']}") for item in debtors_data]
    return []

@app.callback(
    Output('weekly-summary-graph', 'figure'),
    Input("update-summary-btn", "n_clicks"),
)
def update_weekly_summary(n_clicks):
    if n_clicks:
        one_week_ago = datetime.now() - timedelta(days=7)
        recent_inventory = [item for item in inventory_data if datetime.strptime(item["stocked_date"], "%Y-%m-%d") >= one_week_ago]
        total_inventory_added = len(recent_inventory)
        recent_sales = [sale for sale in sales_data if datetime.strptime(sale["sale_date"], "%Y-%m-%d") >= one_week_ago]
        total_sales_amount = sum(sale["sale_amount"] for sale in recent_sales)
        recent_debtors = [debtor for debtor in debtors_data if datetime.strptime(debtor["debtor_date"], "%Y-%m-%d") >= one_week_ago]
        total_debtors_amount = sum(debtor["debtor_amount"] for debtor in recent_debtors)
        total_new_debtors = len(recent_debtors)

        summary_data = {
            "Category": ["Inventory Added", "Sales Amount", "New Debtors", "Debtors Amount"],
            "Total": [total_inventory_added, total_sales_amount, total_new_debtors, total_debtors_amount]
        }
        summary_df = pd.DataFrame(summary_data)
        fig = px.bar(summary_df, x="Category", y="Total", title="Weekly Summary")

        return fig
    return px.bar(title="No data")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run_server(host='0.0.0.0', port=port)
