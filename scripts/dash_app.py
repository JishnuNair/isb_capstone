# -*- coding: utf-8 -*-
import dash
import datetime
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.plotly as py
import plotly.graph_objs as go

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

senti_df = pd.read_csv('/home/jishnu/Documents/ISB/Term3/capstone/repo/isb_capstone-master/repo/sentiment_counts.csv')

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(children=[
    html.H1(children='Analysis of Risk Factors'),

    html.Div(children='''
        Please select company ticker below:
    '''),
    dcc.Dropdown(
    	id = 'ticker_dropdown',
    	options = [
    	{'label' : 'Apple Inc', 'value' : 'aapl'},
    	{'label' : 'NVIDIA Corporation', 'value' : 'nvda'}
    	],
    	value = 'aapl'
    	),

    dcc.Graph(
        id='sentiment-graph'
    )
])

@app.callback(
    dash.dependencies.Output('sentiment-graph', 'figure'),
    [dash.dependencies.Input('ticker_dropdown', 'value')])
def update_sentiment_figure(select_ticker):
	filtered_df = senti_df.loc[senti_df['TICKER'] == select_ticker]
	filtered_df['YEAR'] = filtered_df['YEAR'].apply(lambda x:datetime.datetime(year=x,month=1,day=1))
	filtered_df.sort_values(by=['YEAR'],axis=0,inplace=True)
	data = [go.Scatter(
			x=pd.to_datetime(filtered_df['YEAR']),
			y=filtered_df['POS_CNT'],
			name = "Positive Count",
			)]

	figure = go.Figure(data = data)

	return figure

if __name__ == '__main__':
    app.run_server(debug=True)
