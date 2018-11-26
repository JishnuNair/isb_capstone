# -*- coding: utf-8 -*-
import dash
import datetime
import dash_core_components as dcc
import dash_html_components as html
import dash_table
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

companies = pd.read_csv('/home/jishnu/Documents/ISB/Term3/capstone/repo/isb_capstone-master/repo/companies.csv')
companies = companies[['Company Name','Ticker']]
companies.columns = ['label','value']
companies['value'] = companies['value'].str.lower()

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(children=[
    html.H1(children='Analysis of Risk Factors'),

    html.Div(children='''
        Please select company ticker and year below:
    '''),
    dcc.Dropdown(
    	id = 'ticker_dropdown',
    	options = companies.to_dict("rows"),
    	value = 'aapl'
    	),
    dcc.Dropdown(
    	id = 'year_dropdown',
    	options = [
    	{'label' : '2015', 'value' : '2015'},
    	{'label' : '2016', 'value' : '2016'},
    	{'label' : '2017', 'value' : '2017'},
    	{'label' : '2018', 'value' : '2018'}
    	],
    	value = '2015'
    	),
    html.H3(children='Sentiment Analysis',
    	style={'textAlign' : 'left'}
    	),
    html.Div(children="""
    	Trend of overall sentiment calculated using Loughran McDonald dictionary.
    	"""),
    dcc.Graph(
        id='sentiment-graph'
    ),
    html.H3(children='Document Similarity',
    	style={'textAlign' : 'left'}
    	),
    html.Div(children="""
    	Document similarity for disclosures from same company over the years. Cosine similarity is used as distance metric. 

    	The above selected year is used as baseline for calculating similarity.
    	"""),
    dcc.Graph( id = 'similarity-trend'
    	),
    html.H3(children='Top 10 most similar documents',
    	style={'textAlign' : 'left'}
    	),
    html.Div(children="""
    	The top 10 most similar documents across the companies is obtained using the calculated cosine similarity matrix.
    	"""),
    html.Div(id='dash-table')

])

@app.callback(
    dash.dependencies.Output('dash-table', 'children'),
    [dash.dependencies.Input('ticker_dropdown', 'value'),
    dash.dependencies.Input('year_dropdown', 'value')
    ])
def update_table(select_ticker,select_year):
	column = '{0}_{1}'.format(select_year,select_ticker)
	table_df = sim_df[sim_df['Document'].str.contains(select_ticker) == False].nlargest(10,column)[['Document',column]]
	table_df.columns = ['Document','Similarity']
	table_df['Year'] = table_df['Document'].str.split('_').str.get(0)
	table_df['Ticker'] = table_df['Document'].str.split('_').str.get(1)
	table_df['Company'] = table_df.apply(lambda row: companies.loc[companies['value'] == row['Ticker'],'label'].item(),axis=1)
	# return table_df.to_dict("rows")
	# print(table_df)
	return dash_table.DataTable(id = 'top-table',
    	columns=[{"name": i, "id": i} for i in ['Document','Company','Year','Similarity']],
    	data=table_df[['Document','Company','Year','Similarity']].to_dict("rows")
    	)

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
    [dash.dependencies.Input('ticker_dropdown', 'value'),
    dash.dependencies.Input('year_dropdown', 'value')
    ])
def update_simi_figure(select_ticker,select_year):
	filtered_df = sim_df[sim_df['Document'].str.contains(select_ticker)]
	filtered_df['Year'] = filtered_df['Document'].str.split('_').str.get(0)
	columns = ['Year']
	for year in ['2015','2016','2017','2018']:
		columns.append('{0}_{1}'.format(year,select_ticker))
	filtered_df = filtered_df[filtered_df.columns.intersection(columns)]
	filtered_df.sort_values(by=['Year'],axis=0,inplace=True)
	select_year = '{0}_{1}'.format(select_year,select_ticker)
	if select_year not in filtered_df.columns:
		filtered_df[select_year] = 0
	# filtered_df['prev_sim'] = 0
	# for year in filtered_df['Year']:
	# 	if '{0}_{1}'.format(int(year) - 1,select_ticker) in filtered_df.columns:
	# 		filtered_df.loc[filtered_df['Year'] == year,'prev_sim'] = filtered_df.loc[filtered_df['Year'] == year,'{0}_{1}'.format(int(year)-1,select_ticker)]
	filtered_df['Year'] = filtered_df['Year'].apply(lambda x:datetime.datetime(year=int(x),month=1,day=1))
	data = [go.Scatter(
			x=pd.to_datetime(filtered_df['Year']),
			y=filtered_df[select_year],
			name = "Similarity trend",
			)]
	layout = go.Layout( title = 'Trend of Document Similarity in Risk Factors for {0}'.format(select_ticker))
	figure = go.Figure(data = data, layout = layout)
	return figure


if __name__ == '__main__':
    app.run_server(debug=True)
