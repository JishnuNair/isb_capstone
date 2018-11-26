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

senti_df = pd.read_csv('repo/sentiment_counts.csv')
# senti_df = pd.read_csv('/home/jishnu/Documents/ISB/Term3/capstone/repo/isb_capstone-master/repo/sentiment_counts.csv')
senti_df['OV_POS'] = (senti_df['POS_CNT'] + senti_df['MODAL_STR_CNT']) / senti_df['TOT_CNT']
senti_df['OV_NEG'] = (senti_df['NEG_CNT'] + senti_df['CONSTR_CNT'] + senti_df['LITI_CNT'] + senti_df['UNCERT_CNT'] + senti_df['MODAL_WEA_CNT']) / senti_df['TOT_CNT']
senti_df['OV_SENTI'] = senti_df['OV_POS'] - senti_df['OV_NEG']

sim_df = pd.read_csv('repo/cosine_sim_matrix.csv')
# sim_df = pd.read_csv('/home/jishnu/Documents/ISB/Term3/capstone/repo/isb_capstone-master/repo/cosine_sim_matrix.csv')

companies = pd.read_csv('repo/companies.csv')
# companies = pd.read_csv('/home/jishnu/Documents/ISB/Term3/capstone/repo/isb_capstone-master/repo/companies.csv')
companies = companies[['Company Name','Ticker']]
companies.columns = ['label','value']
companies['value'] = companies['value'].str.lower()

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

server = app.server

app.layout = html.Div(children=[
    html.H1(children='Analysis of Risk Factors'),

    html.Div(children='''
        Please select company ticker and year below:
    '''),
    dcc.Dropdown(
    	id = 'ticker_dropdown',
    	options = companies.to_dict("rows"),
    	value = ['aapl'],
    	multi = True
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
    	The top 10 most similar documents(for each of the selected companies) across the companies is obtained using the calculated cosine similarity matrix.
    	"""),
    html.Div(id='dash-table')

])

@app.callback(
    dash.dependencies.Output('dash-table', 'children'),
    [dash.dependencies.Input('ticker_dropdown', 'value'),
    dash.dependencies.Input('year_dropdown', 'value')
    ])
def update_table(select_ticker,select_year):
	df = pd.DataFrame(columns=['Selected','Similar Document','Year','Similarity'])
	for i, ticker in enumerate(select_ticker):
		column = '{0}_{1}'.format(select_year,ticker)
		table_df = sim_df[sim_df['Document'].str.contains(ticker) == False].nlargest(10,column)[['Document',column]]
		table_df.columns = ['Document','Similarity']
		table_df['Year'] = table_df['Document'].str.split('_').str.get(0)
		table_df['Ticker'] = table_df['Document'].str.split('_').str.get(1)
		table_df['Similar Document'] = table_df.apply(lambda row: companies.loc[companies['value'] == row['Ticker'],'label'].item(),axis=1)
		table_df['Selected'] = column
		df = pd.concat([df,table_df[['Selected','Similar Document','Year','Similarity']]])
	return dash_table.DataTable(id = 'top-table',
    	columns=[{"name": i, "id": i} for i in ['Selected','Similar Document','Year','Similarity']],
    	data=df[['Selected','Similar Document','Year','Similarity']].to_dict("rows")
    	)

@app.callback(
    dash.dependencies.Output('sentiment-graph', 'figure'),
    [dash.dependencies.Input('ticker_dropdown', 'value')])
def update_sentiment_figure(select_ticker):
	data = []
	for i, ticker in enumerate(select_ticker):
		filtered_df = senti_df.loc[senti_df['TICKER'] == ticker]
		filtered_df['FILING_DATE'] = filtered_df['FILING_DATE'].apply(lambda x:datetime.datetime(year=int(x.split('-')[0]),month=int(x.split('-')[1]),day=int(x.split('-')[2])))
		filtered_df.sort_values(by=['FILING_DATE'],axis=0,inplace=True)
		data.append({
			'x' : pd.to_datetime(filtered_df['FILING_DATE']),
			'y' : filtered_df['OV_SENTI'],
			'name' : ticker
			}
			)
		
	layout = go.Layout( title = 'Trend of Overall Sentiment in Risk Factors for {0}'.format(",".join(select_ticker)))
	figure = go.Figure(data = data, layout = layout)
	return figure

@app.callback(
    dash.dependencies.Output('similarity-trend', 'figure'),
    [dash.dependencies.Input('ticker_dropdown', 'value'),
    dash.dependencies.Input('year_dropdown', 'value')
    ])
def update_simi_figure(select_ticker,select_year):
	data = []
	for i, ticker in enumerate(select_ticker):
		filtered_df = sim_df[sim_df['Document'].str.contains(ticker)]
		filtered_df['Year'] = filtered_df['Document'].str.split('_').str.get(0)
		filtered_df['Year'] = filtered_df['Document'].apply(lambda x:senti_df.loc[(senti_df['TICKER'] == x.split('_')[1]) & (senti_df['YEAR'] == int(x.split('_')[0]))]['FILING_DATE'].tolist()[0])
		columns = ['Year']
		for year in ['2015','2016','2017','2018']:
			columns.append('{0}_{1}'.format(year,ticker))
		filtered_df = filtered_df[filtered_df.columns.intersection(columns)]
		filtered_df.sort_values(by=['Year'],axis=0,inplace=True)
		year = '{0}_{1}'.format(select_year,ticker)
		if year not in filtered_df.columns:
			filtered_df[year] = 0
		data.append({
			'x' : pd.to_datetime(filtered_df['Year']),
			'y' : filtered_df[year],
			'name' : ticker
			})
	layout = go.Layout( title = 'Trend of Document Similarity in Risk Factors for {0}'.format(",".join(select_ticker)))
	figure = go.Figure(data = data, layout = layout)
	return figure



if __name__ == '__main__':
    app.run_server(debug=True)
