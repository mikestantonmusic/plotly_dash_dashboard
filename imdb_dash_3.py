# import libraries

import dash
from dash import Dash
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_core_components as dcc
import pandas as pd
import numpy as np
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import plotly.express as px

# define colors

chart_color = 'white'
text_color = 'cadetblue'
graph_bg_color = 'whitesmoke'
gridline_color = 'whitesmoke'
bar_color = 'peachpuff'

# import and clean the data

df = pd.read_csv('imdb.csv')
df['Duration'] = df['Duration'].astype(str).str.replace('None','0')
df['Duration'] = df['Duration'].astype(float)
df['Rate'] = df['Rate'].astype(str).str.replace('No Rate','0')
df['Rate'] = df['Rate'].astype('float64')
df['Votes'] = df['Votes'].astype(str).str.replace(',','')
df['Votes'] = df['Votes'].astype(str).str.replace('No Votes','0')
df['Votes'] = df['Votes'].astype(int)

# rearrange the data for visualization

def group_table(column, sort_column='Votes'):
    data = df.loc[:,[column,'Rate','Votes']].groupby(column).agg(np.mean).reset_index()
    data = data.sort_values(by = [sort_column], ascending=False).reset_index(drop=True)
    return data
    
def votes_table():
    votes_df = df.loc[:,['Rate','Votes']].groupby('Votes').agg(np.mean).reset_index()
    votes_df = votes_df.sort_values(by = ['Votes'], ascending=False).reset_index(drop=True)
    return votes_df

def genre_table():
    genres = []
    for genre_str in df['Genre']:
        genre_list = genre_str.split(', ')
        genres.extend(genre_list)
    unique_genres = list(set(genres))
    genre_rate_list = []
    genre_votes_list = []
    for genre in unique_genres:
        genre_rate_list.append(df.loc[df['Genre'].str.contains(genre), 'Rate'].mean())
        genre_votes_list.append(df.loc[df['Genre'].str.contains(genre), 'Votes'].mean())
    genre_dict = {'Genre':unique_genres, 'Rate': genre_rate_list, 'Votes': genre_votes_list}
    genre_df = pd.DataFrame(genre_dict)
    genre_df = genre_df.sort_values(by = ['Votes'], ascending=False).reset_index(drop=True)
    return genre_df

# define the logic for creating graphs in the dashboard

def drawGraph(data, x_data, y_data, type, graph_title, X_title, Y_title, figwidth=12):
    if type=='line':
        graph_ = go.Scatter(x=data[x_data], y=data[y_data], marker=dict(color=bar_color), showlegend=False)
    elif type=='bar':
        graph_ = go.Bar(x=data[x_data], y=data[y_data], marker=dict(color=bar_color), showlegend=False)
    elif type=='scatter':
        graph_ = go.Scatter(x=data[x_data], y=data[y_data], mode='markers', marker=dict(color=bar_color), showlegend=False)
    layout_ = go.Layout(
        title=graph_title, 
        plot_bgcolor=chart_color, 
        paper_bgcolor=chart_color,
        title_font=dict(color=text_color),
        xaxis=dict(title=X_title,
                title_font=dict(color=text_color),
                tickfont=dict(color=text_color),
                gridcolor=gridline_color),
        yaxis=dict(title=Y_title,
                title_font=dict(color=text_color),
                tickfont=dict(color=text_color),
                gridcolor=gridline_color))
    figure_obj = dbc.Col(
        html.Div([
            dbc.Card(
                dbc.CardBody(
                    dcc.Graph(
                        figure=go.Figure(data=graph_, layout=layout_),
                        style={'margin-bottom': '20px'})
                )
            )
        ]),width=figwidth
    )
    return figure_obj
         
# define the logic for creating text boxes 

def drawText(text, textwidth=12):
    text_obj = dbc.Col([
        html.Div([
            dbc.Card(
                dbc.CardBody([
                    html.Div([
                        html.H2(text),
                    ], style={'textAlign': 'center'}) 
                ])
            ),
        ])
    ], width=textwidth)
    return text_obj  

# create the app for the dashboard and establish the layout for the dashboard
                                                                     
app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div([
    dcc.Tabs(style={'backgroundColor': graph_bg_color, 'padding': '20px'},id='tabs', value='tab-1', children=[
        dcc.Tab(label='Ratings', value='tab-1', style={'font-family': 'Arial', 'color': text_color},selected_style={'font-family': 'Arial', 'color': text_color, 'fontWeight': 'bold'}),
        dcc.Tab(label='Votes', value='tab-2', style={'font-family': 'Arial', 'color': text_color},selected_style={'font-family': 'Arial', 'color': text_color, 'fontWeight': 'bold'}),
    ]),
    html.Div(id='tab-content', style={'color':text_color, 'backgroundColor':graph_bg_color, 'padding':'20px'})
])

@app.callback(
    dash.dependencies.Output('tab-content', 'children'),
    [dash.dependencies.Input('tabs', 'value')]
)

# tab 1

def render_content(tab):
    if tab == 'tab-1':
        return html.Div([
            dbc.Row([drawText('Average Rating Analysis')], align='center'),
            html.Br(),
            dbc.Row([drawGraph(group_table('Duration', 'Duration'),'Duration','Rate','line','title','xaxis','yaxis')]), 
            html.Br(),
            dbc.Row([drawGraph(group_table('Certificate'),'Certificate','Rate','bar','title','xaxis','yaxis')]), 
            html.Br(),
            dbc.Row([
                drawGraph(group_table('Nudity'),'Nudity','Rate','bar','title','xaxis','yaxis',6), 
                drawGraph(group_table('Violence'),'Violence','Rate','bar','title','xaxis','yaxis',6),
                #align='center'
                ]),
            html.Br(), 
            dbc.Row([
                drawGraph(group_table('Profanity'),'Profanity','Rate','bar','title','xaxis','yaxis',6), 
                drawGraph(group_table('Alcohol'),'Alcohol','Rate','bar','title','xaxis','yaxis',6),
                #align='center'
                ]),
            html.Br(),                        
            dbc.Row([drawGraph(group_table('Frightening'),'Frightening','Rate','bar','title','xaxis','yaxis')]), 
            html.Br(),
            dbc.Row([drawGraph(group_table('Date', 'Date'),'Date','Rate','line','title','xaxis','yaxis')]), 
            html.Br(),
            dbc.Row([drawGraph(genre_table(),'Genre','Rate','bar','title','xaxis','yaxis')]), 
            html.Br(),
            dbc.Row([drawGraph(votes_table(),'Votes','Rate','scatter','title','xaxis','yaxis')]), 
            html.Br()   
        ]),

# tab 2

    elif tab == 'tab-2':
        return html.Div([
            dbc.Row([drawText('Average Rating Analysis')], align='center'),
            html.Br(),
            dbc.Row([drawGraph(group_table('Duration', 'Duration'),'Duration','Votes','line','title','xaxis','yaxis')]), 
            html.Br(),
            dbc.Row([drawGraph(group_table('Certificate'),'Certificate','Votes','bar','title','xaxis','yaxis')]), 
            html.Br(),
            dbc.Row([
                drawGraph(group_table('Nudity'),'Nudity','Votes','bar','title','xaxis','yaxis',6), 
                drawGraph(group_table('Violence'),'Violence','Votes','bar','title','xaxis','yaxis',6),
                #align='center'
                ]),
            html.Br(), 
            dbc.Row([
                drawGraph(group_table('Profanity'),'Profanity','Votes','bar','title','xaxis','yaxis',6), 
                drawGraph(group_table('Alcohol'),'Alcohol','Votes','bar','title','xaxis','yaxis',6),
                #align='center'
                ]),
            html.Br(),                        
            dbc.Row([drawGraph(group_table('Frightening'),'Frightening','Votes','bar','title','xaxis','yaxis')]), 
            html.Br(),
            dbc.Row([drawGraph(group_table('Date', 'Date'),'Date','Votes','line','title','xaxis','yaxis')]), 
            html.Br(),
            dbc.Row([drawGraph(genre_table(),'Genre','Votes','bar','title','xaxis','yaxis')]), 
            html.Br(),
            dbc.Row([drawGraph(votes_table(),'Rate','Votes','scatter','title','xaxis','yaxis')]), 
            html.Br()   
        ]),

# run the app

app.run_server(debug=True)



