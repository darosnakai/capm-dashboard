from dash import Dash, html, dcc, dash_table, Input, Output, State
import plotly.express as px
import pandas as pd
from dash.exceptions import PreventUpdate
import time
from tickers_analysis import analyzer
import traceback

start_time = time.time()

app = Dash(__name__)

colors = {
    'background': '#F5F5DC',
    'text': '#111111'
}

# Function to get SP500 tickers
def get_sp500_tickers():
    try:
        all_stocks = pd.read_html("data/sp500_components.html")[0]
        
        #get value at rows i, column 0 (first column)
        all_tickers = [all_stocks.iloc[i, 0] for i in range(len(all_stocks))]
        
        # Create dropdown options
        ticker_options = [{'label': ticker, 'value': ticker} for ticker in all_tickers]
        return ticker_options
    
    except Exception as e:
        print(f"Error loading tickers: {e}")
        fallback_tickers = ["AAPL", "NVDA", "TSLA", "AMZN", "MSFT", "GOOG", "INTC"]
        return [{'label': ticker, 'value': ticker} for ticker in fallback_tickers]


# Get ticker options
ticker_options = get_sp500_tickers()

#app.layout is the UI components of the application
app.layout = html.Div(style={'backgroundColor': colors['background']}, children=[
    #subtitle of the application, aligned to the center
    html.H1('CAPM Modeling Function', style={
        'textAlign': 'center',
        'color': colors['text'],
        'marginBottom': '20px',
        'fontSize':'25px'
    }),

    dcc.Markdown('''
    **What is CAPM?**
    
    CAPM (Capital Asset Pricing Model) is a financial model developed to evaluate an asset's price, it involves calculating an
                 asset's price based on the risk relationship (volatility) with a particular market. 
    > **CAPM formula:** *E(rA) = rf + βA × (E(rm) - rf)*
    
    - Beta: represents the asset's sensitivity to market movements, essentially showing us the systemic risk of this asset (its volatility compared to a given market)
    - rf: Refers to the risk free rate. We are using Treasury Bills 10yr interest rate (around 4,2%)
    - E(rm): Refers to the expected return of the market. We are using the historical return of the given market selected by the user
    
    *This model is using the S&P500 index as the reference market*
'''),


    html.Div([
        html.Div("Select the information for the model:", style={
            'color': colors['text'],
            'marginBottom': '15px',
            'fontSize': '18px'
        }),
        
        # Period selection with RadioItems
        html.Div([
            html.Label('Period Selection', style={'color': colors['text']}),
            dcc.RadioItems(
                id='period-radioitem',  # name of the feature
                options=[
                    {'label': '1 Year', 'value': '1y'},
                    {'label': '2 Years', 'value': '2y'},
                    {'label': '3 Years', 'value': '3y'},
                    {'label': '5 Years', 'value': '5y'},
                    {'label': '10 Years', 'value': '10y'},
                    {'label': '20 Years', 'value': '20y'}
                ],
                value='5y',  # default value
                style={'color': colors['text'], 'marginTop': '10px'}
            ),
        ], style={'width': '31%', 'display': 'inline-block', 'marginBottom': '20px'}),
        
        # Interval selection with RadioItems
        html.Div([
            html.Label('Interval Selection', style={'color': colors['text']}),
            dcc.RadioItems(
                id='interval-radioitem',  # name of the feature
                options=[
                    {'label': 'Daily', 'value': '1d'},
                    {'label': 'Weekly', 'value': '1wk'},
                    {'label': 'Monthly', 'value': '1mo'}
                ],
                value='1mo',  # default value
                style={'color': colors['text'], 'marginTop': '10px'}
            ),
        ], style={'width': '31%', 'display': 'inline-block', 'marginBottom': '20px'}),
    
        # Ticker selection with dropdown
        html.Div([
            html.Label('Select the Stocks you want to analyze', style={'color': colors['text']}),
            dcc.Dropdown(
                id='ticker-dropdown',
                options=ticker_options,
                multi=True,
                placeholder="Select tickers to analyze",
                style={'color': colors['text'], 'backgroundColor': colors['background']}
            ),
        ], style={'marginBottom': '20px'}),
        
        
        # Run Analysis button
        html.Button('Run Analysis', id='run-button', style={
            'backgroundColor': '#4CAF50',
            'color': 'white',
            'padding': '10px 15px',
            'margin': '10px 0',
            'border': 'none',
            'borderRadius': '4px',
            'cursor': 'pointer',
            'fontSize': '16px'
        }),
        
        # Loading message and output container
        html.Div(id='loading-message', style={'color': colors['text'], 'marginTop': '10px'}),
        html.Div(id='output-container', style={'color': colors['text'], 'marginTop': '20px'})
    ])
])

def create_data_table(df):
    return dash_table.DataTable(
        data=df.reset_index().to_dict('records'),
        columns=[{'name': col, 'id': col} for col in df.reset_index().columns],
        style_cell={
            'backgroundColor': colors['background'],
            'color': colors['text'],
            'textAlign': 'left',
            'padding': '7px'
        },
        style_header={
            'backgroundColor': '#333333',
            'color': 'white',
            'fontWeight': 'bold'
        },
        page_size=10,
        style_table={'overflowX': 'auto'},
    )

# Callback for the "Run Analysis" button
@app.callback(
    [Output('loading-message', 'children'),
     Output('output-container', 'children')],
    [Input('run-button', 'n_clicks')],
    [State('period-radioitem', 'value'),
     State('interval-radioitem', 'value'),
     State('ticker-dropdown', 'value')],
    prevent_initial_call=True
)
def update_output(n_clicks, period, interval, selected_tickers):
    if n_clicks is None:
        raise PreventUpdate
    
    # Check if tickers were selected
    if not selected_tickers or len(selected_tickers) == 0:
        return (
            html.Div("No tickers selected!"), 
            html.Div("Please select tickers using the dropdown above before running the analysis.")
        )

    # Show loading message
    loading_message = f"Running analysis with {len(selected_tickers)} tickers, {period} period, {interval} interval..."
    html.Div(loading_message)
    
    try:
        # Create analyzer instance
        tickers_instance = analyzer()
        
        tickers_instance.number_of_tickers = len(selected_tickers)
        tickers_instance.period = period
        tickers_instance.interval = interval
        tickers_instance.index_processor.period = period
        tickers_instance.index_processor.interval = interval
        tickers_instance.index_processor.number_of_tickers = len(selected_tickers)

        #first calling the returns data to populate the returns df:
        returns_data = tickers_instance.returns_all_tickers(selected_tickers)

        #fetching the ticker names:
        ticker_names = tickers_instance.get_stock_ticker_names()

        # Run the full analysis using the analyzer class
        all_info = tickers_instance.run_all_analysis()
        
        # Create visualizations
        # Beta comparison bar chart
        beta_col = f"Beta {period} {interval}"
        
        
        # Create CAPM vs Beta scatter plot
        if "Expected Monthly Returns (%)" in all_info.columns:
            capm_beta_df = all_info.reset_index()[['Ticker', "Expected Monthly Returns (%)", beta_col]]
            capm_beta_df = capm_beta_df.rename(columns={
                "Expected Monthly Returns (%)": 'Expected Return',
                beta_col: 'Beta'
            })
            
            scatter_fig = px.scatter(
                capm_beta_df,
                x='Beta',
                y='Expected Return',
                text='Ticker',
                title='CAPM Expected Return vs Beta',
                labels={'Beta': 'Beta', 'Expected Return': 'Expected Monthly Return (%)'}
            )
            
            scatter_fig.update_traces(
                textposition='top center',
                marker=dict(size=12, opacity=0.8)
            )
            
            scatter_fig.update_layout(
                plot_bgcolor=colors['background'],
                paper_bgcolor=colors['background'],
                font_color=colors['text']
            )
            
            scatter_chart = dcc.Graph(figure=scatter_fig)
        else:
            scatter_chart = html.Div("CAPM vs Beta chart not available")
        
        # Return components to display
        return html.Div("Analysis completed!"), html.Div([
            html.H4('CAPM and Beta Analysis Results', style={'color': colors['text']}),
            create_data_table(all_info),
            html.H4('CAPM vs Beta Relationship', style={'color': colors['text'], 'marginTop': '20px'}),
            scatter_chart
        ])
    
    except Exception as e:
        error_trace = traceback.format_exc()
        return html.Div("Analysis completed with errors."), html.Div([
            html.H4('Error in Analysis', style={'color': '#FF6B6B'}),
            html.Pre(f"Error: {str(e)}", style={'color': '#FF6B6B'}),
            html.Pre(error_trace, style={'color': '#FF6B6B', 'fontSize': '12px'})
        ])

if __name__ == '__main__':
    app.run_server(debug=True)
    print("Process finished --- %s seconds ---" % (time.time() - start_time))