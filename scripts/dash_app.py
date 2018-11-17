# -*- coding: utf-8 -*-
import dash
import datetime
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.plotly as py
import plotly.graph_objs as go

pd.options.mode.chained_assignment = None

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

senti_df = pd.read_csv('/home/jishnu/Documents/ISB/Term3/capstone/repo/isb_capstone-master/repo/sentiment_counts.csv')
senti_df['OV_POS'] = (senti_df['POS_CNT'] + senti_df['MODAL_STR_CNT']) / senti_df['TOT_CNT']
senti_df['OV_NEG'] = (senti_df['NEG_CNT'] + senti_df['CONSTR_CNT'] + senti_df['LITI_CNT'] + senti_df['UNCERT_CNT'] + senti_df['MODAL_WEA_CNT']) / senti_df['TOT_CNT']
senti_df['OV_SENTI'] = senti_df['OV_POS'] - senti_df['OV_NEG']

sim_df = pd.read_csv('/home/jishnu/Documents/ISB/Term3/capstone/repo/isb_capstone-master/repo/cosine_sim_matrix.csv')

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
    ),
    dcc.Graph( id = 'similarity-trend'
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
			y=filtered_df['OV_SENTI'],
			name = "Overall Sentiment",
			)]
	layout = go.Layout( title = 'Trend of Overall Sentiment in Risk Factors for {0}'.format(select_ticker))
	figure = go.Figure(data = data, layout = layout)
	return figure

@app.callback(
    dash.dependencies.Output('similarity-trend', 'figure'),
    [dash.dependencies.Input('ticker_dropdown', 'value')])
def update_simi_figure(select_ticker):
	filtered_df = sim_df[sim_df['Document'].str.contains(select_ticker)]
	filtered_df['Year'] = filtered_df['Document'].str.split('_').str.get(0)
	columns = ['Year']
	for year in ['2015','2016','2017','2018']:
		columns.append('{0}_{1}'.format(year,select_ticker))
	filtered_df = filtered_df[filtered_df.columns.intersection(columns)]
	filtered_df.sort_values(by=['Year'],axis=0,inplace=True)
	filtered_df['prev_sim'] = 0
	for year in filtered_df['Year']:
		if '{0}_{1}'.format(int(year) - 1,select_ticker) in filtered_df.columns:
			filtered_df.loc[filtered_df['Year'] == year,'prev_sim'] = filtered_df.loc[filtered_df['Year'] == year,'{0}_{1}'.format(int(year)-1,select_ticker)]
	filtered_df['Year'] = filtered_df['Year'].apply(lambda x:datetime.datetime(year=int(x),month=1,day=1))
	data = [go.Scatter(
			x=pd.to_datetime(filtered_df['Year']),
			y=filtered_df['prev_sim'],
			name = "Similarity trend",
			)]
	layout = go.Layout( title = 'Trend of Document Similarity in Risk Factors for {0}'.format(select_ticker))
	figure = go.Figure(data = data, layout = layout)
	return figure

if __name__ == '__main__':
    app.run_server(debug=True)
