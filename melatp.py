import dash
import dash_bootstrap_components as dbc
from dash import html, dcc
from dash.dependencies import Input, Output, State
from datetime import datetime, timedelta
import base64
import io
import firebase_admin
from firebase_admin import credentials, initialize_app, firestore

# Initialize Firebase
import os
import json
firebase_credentials = os.getenv('FIREBASE_CONFIG')
if firebase_credentials:
    cred_dict = json.loads(firebase_credentials)
    cred = credentials.Certificate(cred_dict)
    initialize_app(cred)
else:
    print("Firebase credentials not found in environment variables")
db = firestore.client()

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Initialize data lists
inventory_data = []
sales_data = []
debtors_data = []

app.layout = dbc.Container([
    html.H1('WELCOME TO JUSMEL BEAUTY HAVEN'),
    html.P('Manage your sales, inventory, and debtors efficiently.'),

    dbc.Row([
        dbc.Col(html.Div([
            html.H4('Inventory Management'),
            html.P("Date stocked, source, perfume name, amount paid, quantity, gender, description, image, comments."),
            dbc.Form([
                dbc.Row([
                    dbc.Col(dbc.Input(id='stocked-date', type='date', placeholder='Date Stocked'), width=3),
                    dbc.Col(dbc.Input(id='source', type='text', placeholder='Source'), width=3),
                    dbc.Col(dbc.Input(id='perfume-name-inventory', type='text', placeholder='Perfume Name'), width=3),
                    dbc.Col(dbc.Input(id='amount-paid', type='number', placeholder='Amount Paid'), width=3),
                ]),
                dbc.Row([
                    dbc.Col(dbc.Input(id='quantity', type='number', placeholder='Quantity'), width=3),
                    dbc.Col(dbc.Select(
                        id='gender',
                        options=[
                            {'label': 'Masculine', 'value': 'Masculine'},
                            {'label': 'Feminine', 'value': 'Feminine'},
                            {'label': 'Unisex', 'value': 'Unisex'}
                        ],
                        placeholder='Gender'
                    ), width=3),
                    dbc.Col(dbc.Input(id='description', type='text', placeholder='Description'), width=6),
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
                    ), width=6),
                    dbc.Col(dbc.Input(id='comments', type='text', placeholder='Comments'), width=6),
                ]),
                dbc.Button('Add to Inventory', id='add-inventory-btn', color='primary', className='mt-2'),
            ])
        ]), width=4),

        dbc.Col(html.Div([
            html.H5("Inventory List"),
            html.Div(id='inventory-list'),
        ]), width=8)
    ]),

    dbc.Row([
        dbc.Col(html.Div([
            html.H4('Sales Tracking'),
            html.P('Date sold, buyer name, perfume name, amount, comments.'),
            dbc.Form([
                dbc.Row([
                    dbc.Col(dbc.Input(id="sale-date", type='date', placeholder='Date Sold'), width=3),
                    dbc.Col(dbc.Input(id='buyer-name', type='text', placeholder='Buyer Name'), width=3),
                    dbc.Col(dbc.Input(id='perfume-name-sale', type='text', placeholder='Perfume Name'), width=3),
                    dbc.Col(dbc.Input(id='sale-amount', type='number', placeholder='Amount'), width=3),
                ]),
                dbc.Row([
                    dbc.Col(dbc.Input(id='sale-comments', type='text', placeholder='Comments'), width=12),
                ]),
                dbc.Button('Record Sale', id='record-sale-btn', color='success', className='mt-2'),
            ])
        ]), width=4),

        dbc.Col(html.Div([
            html.H5('Sales List'),
            html.Ul(id="sales-list")
        ]), width=8)
    ]),

    dbc.Row([
        dbc.Col(html.Div([
            html.H4('Debtors Management'),
            html.P('Debtor name, telephone number, date, comments.'),
            dbc.Form([
                dbc.Row([
                    dbc.Col(dbc.Input(id='debtor-name', type='text', placeholder='Debtor Name'), width=4),
                    dbc.Col(dbc.Input(id='debtor-phone', type='text', placeholder='Telephone Number'), width=4),
                    dbc.Col(dbc.Input(id='debtor-date', type='date', placeholder='Date'), width=4),
                ]),
                dbc.Row([
                    dbc.Col(dbc.Input(id='debtor-comments', type='text', placeholder='Comments'), width=12),
                ]),
                dbc.Button('Add Debtor', id='add-debtor-btn', color='warning', className='mt-2'),
            ])
        ]), width=4),

        dbc.Col(html.Div([
            html.H5('Debtors List'),
            html.Ul(id="debtors-list"),
        ]), width=8)
    ]),

    dbc.Row([
        dbc.Col(html.Div([
            html.H4("Weekly Summaries"),
            html.Div(id="weekly-summary"),
            dbc.Button("Update Summary", id="update-summary-btn", color='info', className='mt-2'),
        ]), width=12)
    ])
], fluid=True)

def parse_contents(contents, filename):
    return html.Div([
        html.H5(filename),
        html.Img(src=contents, style={'height': '200px'}),
    ])

@app.callback(
    Output("inventory-list", 'children'),
    Input("add-inventory-btn", 'n_clicks'),
    State("stocked-date", "value"),
    State("source", "value"),
    State("perfume-name-inventory", "value"),
    State("amount-paid", "value"),
    State("quantity", "value"),
    State("gender", "value"),
    State("description", "value"),
    State("upload-image", "contents"),
    State("upload-image", "filename"),
    State("comments", "value"),
)
def update_inventory_list(n_clicks, stocked_date, source, perfume_name_inventory, amount_paid, quantity, gender, description, image_contents, filename, comments):
    if n_clicks:
        inventory_item = {
            "stocked_date": stocked_date,
            "source": source,
            "perfume_name_inventory": perfume_name_inventory,
            "amount_paid": amount_paid,
            "quantity": quantity,
            "gender": gender,
            "description": description,
            "image_contents": image_contents,
            "filename": filename,
            "comments": comments
        }
        db.collection('inventory').add(inventory_item)
        inventory_data.append(inventory_item)
        return [html.Div([
            html.P(f"Date Stocked: {item['stocked_date']}"),
            html.P(f"Source: {item['source']}"),
            html.P(f"Perfume Name: {item['perfume_name_inventory']}"),
            html.P(f"Amount Paid: {item['amount_paid']}"),
            html.P(f"Quantity: {item['quantity']}"),
            html.P(f"Gender: {item['gender']}"),
            html.P(f"Description: {item['description']}"),
            parse_contents(item['image_contents'], item['filename']) if item['image_contents'] else html.P("No Image"),
            html.P(f"Comments: {item['comments']}"),
            html.Hr()
        ]) for item in inventory_data]

@app.callback(
    Output("sales-list", 'children'),
    Input("record-sale-btn", 'n_clicks'),
    State("sale-date", "value"),
    State("buyer-name", "value"),
    State("perfume-name-sale", "value"),
    State("sale-amount", "value"),
    State("sale-comments", "value"),
)
def update_sales_list(n_clicks, sale_date, buyer_name, perfume_name_sale, sale_amount, sale_comments):
    if n_clicks:
        sale_item = {
            "sale_date": sale_date,
            "buyer_name": buyer_name,
            "perfume_name_sale": perfume_name_sale,
            "sale_amount": sale_amount,
            "sale_comments": sale_comments
        }
        db.collection('sales').add(sale_item)
        sales_data.append(sale_item)
        return [html.Li(f"Sold on {item['sale_date']} to {item['buyer_name']} for {item['sale_amount']}. Perfume: {item['perfume_name_sale']}. Comments: {item['sale_comments']}") for item in sales_data]

@app.callback(
    Output("debtors-list", "children"),
    Input("add-debtor-btn", 'n_clicks'),
    State("debtor-name", "value"),
    State("debtor-phone", "value"),
    State("debtor-date", "value"),
    State("debtor-comments", "value"),
)
def update_debtors_list(n_clicks, debtor_name, debtor_phone, debtor_date, debtor_comments):
    if n_clicks:
        debtor_item = {
            'debtor_name': debtor_name,
            'debtor_phone': debtor_phone,
            'debtor_date': debtor_date,
            'debtor_comments': debtor_comments
        }
        db.collection('debtors').add(debtor_item)
        debtors_data.append(debtor_item)
        return [html.Li(f"Debtor: {item['debtor_name']}, Phone: {item['debtor_phone']}, Date: {item['debtor_date']}. Comments: {item['debtor_comments']}") for item in debtors_data]

@app.callback(
    Output('weekly-summary', 'children'),
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
        total_new_debtors = len(recent_debtors)
        summary = [
            html.P(f"Total Inventory Added: {total_inventory_added}"),
            html.P(f"Total Sales Amount: {total_sales_amount}"),
            html.P(f"Total New Debtors: {total_new_debtors}"),
        ]

        return summary
    return []
import os

if __name__ == "__main__":
    port =int(os.environ.get("PORT", 10000))
    app.run_server(debug=True, host="0.0.0.0", port=port)
    