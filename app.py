# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table 
from dash.dependencies import Input, Output

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import math
from plotly.subplots import make_subplots

#external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# Plotly mapbox token
mapbox_access_token = "pk.eyJ1IjoicGxvdGx5bWFwYm94IiwiYSI6ImNqdnBvNDMyaTAxYzkzeW5ubWdpZ2VjbmMifQ.TXcBE-xg9BFdV2ocecc_7g"

app = dash.Dash(__name__)

server = app.server
# ================================================================ DATA 

df = pd.read_csv('global_01.csv')
df_show = df[['State','Country','Date','Day_Elapsed','Confirmed','Deaths','Recovered']].sort_values(by=['Date','Confirmed'],ascending=False)
#df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/2014_us_cities.csv')
#print(df[['State','Confirmed','Deaths','Recovered']])

# ================================================================ GENERAL FUNCTION



def generate_geo_map(df):

    lat = df["latitude"].tolist()
    lon = df["longitude"].tolist()
    state_list = df["State"].tolist()
    nation_list = df["Country"].tolist()
    confirmed_list = df["Confirmed"].tolist()
    deaths_list = df["Deaths"].tolist()
    recovered_list = df["Recovered"].tolist()
    #average_confirmed = df["Confirmed"]["mean"].tolist()

    colors = ["#21c7ef", "#76f2ff", "#ff6969", "#ff1717"]

    confirmed_metric_data = {}
    confirmed_metric_data["min"] = df["Confirmed"].min()
    confirmed_metric_data["max"] = sorted(confirmed_list, reverse=True)[1]
    confirmed_metric_data["mid"] = (confirmed_metric_data["min"] + confirmed_metric_data["max"]) / 2
    confirmed_metric_data["low_mid"] = (
        confirmed_metric_data["min"] + confirmed_metric_data["mid"]
    ) / 2
    confirmed_metric_data["high_mid"] = (
        confirmed_metric_data["mid"] + confirmed_metric_data["max"]
    ) / 2



    countries = []

    for i in range(len(lat)):
        #print("CHECK POINT 1 - {}".format(i))
        state = state_list[i]
        nation = nation_list[i]
        confirmed = confirmed_list[i]
        deaths = deaths_list[i]
        recovered = recovered_list[i]

        if confirmed <= confirmed_metric_data["low_mid"]:
            color = colors[0]
        elif confirmed_metric_data["low_mid"] < confirmed <= confirmed_metric_data["mid"]:
            color = colors[1]
        elif confirmed_metric_data["mid"] < confirmed <= confirmed_metric_data["high_mid"]:
            color = colors[2]
        else:
            color = colors[3]

        country = go.Scattermapbox(
            lat=[lat[i]],
            lon=[lon[i]],
            mode="markers",
            marker=dict(
                color=color,
                showscale=True,
                colorscale=[
                    [0, "#21c7ef"],
                    [0.33, "#76f2ff"],
                    [0.66, "#ff6969"],
                    [1, "#ff1717"],
                ],
                size=math.log(confirmed,6)*10,
                opacity=0.7
                ),
            selected=dict(marker={"color": "#ffff00"}),
            hoverinfo="text",
            text=nation
                +"<br>"
                +state
                +"<br>"
                +"Confirmed : {}".format(confirmed)
                +"<br>"
                +"Deaths : {}".format(deaths)
                +"<br>"
                +"Recoverd : {}".format(recovered),
        )
        countries.append(country)

    layout = go.Layout(
        title="Global Map",
        margin=dict(l=10, r=10, t=30, b=10, pad=3),
        plot_bgcolor="white",
        paper_bgcolor="white",
        clickmode="event+select",
        hovermode="closest",
        showlegend=False,
        mapbox=go.layout.Mapbox(
            accesstoken=mapbox_access_token,
            bearing=0,
            center=go.layout.mapbox.Center(
                lat=25, lon=102
            ),
            pitch=20,
            zoom=2,
            #style="mapbox://styles/plotlymapbox/cjvppq1jl1ips1co3j12b9hex",
            style="light"
        ),
    )

    figure = dict(data=countries, layout=layout)

    return figure


# ================================================================ DIV

geo_map = html.Div(
                id="geo-map-loading-outer",
                children=[
                    dcc.Loading(
                        id="loading",
                        children=dcc.Graph(
                            id='geo-map'
                            ),
                        )
                    ],
                ),

day_slider = dcc.Slider(
        id='day-slider',
        min=int(df['Day_Elapsed'].unique()[0]),
        max=int(df['Day_Elapsed'].unique()[-1]),
        value=int(df['Day_Elapsed'].unique()[-1]),
        #marks={str(year): str(year) for year in df['Last Update'].unique()},
        marks={int(j): '{}'.format(i[5:10]) for i,j in zip(df['Date'].unique(),df['Day_Elapsed'].unique())},
        step=1
        ),

nat_options = [{"label": i, "value": i} for i in df['Country'].unique()]

# ================================================================ LAYOUT



app.layout = html.Div([
    
    html.Div([html.H1(children='Novel Corona Virus Dashboard', style={'text-align':'center','margin-top':'30px'})],
            style={'margin-top':'50px'}),

    html.Div([html.H6(children='Last Update : 01-02-2020 ', style={'text-align':'left','margin-left':'10px'})],
            style={'margin-top':'20px'}),

    html.Div([
        html.Div([
            html.Div(children=''' Select Country :  '''),
            dcc.Dropdown(
                id='nat_dropdown',
                options=nat_options,
                multi=False,
                clearable=True,
                className="dcc_control")
            ], className="pretty_container six columns"),
        
        html.Div([
            html.Div(children=" Select the date :  "),
            html.Div(day_slider, style={'margin-top':'30px'})
            ], className="pretty_container six columns")

        ], className="row flex-display"),


    html.Div([
        html.Div([dcc.Graph(id='trend-line')
            ], className="pretty_container six columns"),
        html.Div([
            html.Div([dcc.Graph(id='bar-chart')]),
            ], className="pretty_container six columns"),
        ], className="row flex-display"),

    

    html.Div([
        html.Div([html.Div(id='raw_main_table'),
            ], className="pretty_container six columns"),
        html.Div([dcc.Graph(id='geo-map')
            ],className="pretty_container six columns"),

        ], className="row flex-display"),

    html.Div([html.H6(children='Author : aiden.c.ahn@gmail.com', style={'text-align':'right','margin-top':'10px'})]),
    html.Div([html.H6(children='Data Source : WHO, JHU ', style={'text-align':'right','margin-top':'10px'})]),

])

# ================================================================ CALLBACK

@app.callback(
    Output('geo-map', 'figure'),
    [Input('day-slider', 'value')])
def update_figure(selected_day):

    df2 = df[df['Day_Elapsed'] == selected_day]
    print("Hi - " + str(selected_day))

    return generate_geo_map(df2)


@app.callback(
    Output('raw_main_table', 'children'),
    [Input('nat_dropdown','value')])
def update_figure(country):

    if  country is None: 
        df2 = df_show
    else:
        df2 = df_show[df_show['Country']==country]

    figure = dash_table.DataTable(
                id='main_table',
                columns=[{"name": i, "id": i} for i in df2.columns],
                data=df2.to_dict('records'),
                filter_action="native",
                sort_action="native",
                sort_mode="multi",  
                page_action="native",
                page_current= 0,
                page_size= 10,
                style_table={'overflowX': 'scroll'},
                )

    layout = go.Layout(
        title="Data Table")

    return figure

@app.callback(
    Output('trend-line', 'figure'),
    [Input('nat_dropdown','value')])
def update_figure(country):

    if  country is None: 
        df = df_show
    else:
        df = df_show[df_show['Country']==country]

    df2 = df.groupby('Date')['Confirmed','Deaths','Recovered'].sum()
    day_list = list(df2.index)

    traces = [
        dict(
            type="scatter",
            mode="lines+markers",
            name="Confirmed",
            x=day_list,
            y=df2['Confirmed'],
            line=dict(shape="spline", smoothing=2, width=2, color="#fac1b7"),
            marker=dict(symbol="diamond", size=10),
        ),
        dict(
            type="scatter",
            mode="lines+markers",
            name="Deaths",
            x=day_list,
            y=df2['Deaths'],
            line=dict(shape="spline", smoothing=2, width=2, color="#a9bb95"),
            marker=dict(symbol="circle", size=8),
        ),
        dict(
            type="scatter",
            mode="lines+markers",
            name="Recovered",
            x=day_list,
            y=df2['Recovered'],
            line=dict(shape="spline", smoothing=2, width=2, color="#92d8d8"),
            marker=dict(symbol="triangle", size=8),
        ),
    ]

    layout = go.Layout(
        #autosize= True,
        title="No of Confirmed / Deaths / Recovered",
        margin=dict(l=30, r=30, t=40, b=30, pad=5),
        showlegend=True)

    figure = dict(data=traces, layout=layout)

    return figure


@app.callback(
    Output('bar-chart', 'figure'),
    [Input('day-slider', 'value')])
def update_figure(selected_day):

    df2 = df[(df['Day_Elapsed'] == selected_day) & (df['nat_cod'] != 'CN')]
    df2_CN = df[(df['Day_Elapsed'] == selected_day) & (df['nat_cod'] == 'CN')]
    df2_CN = df2_CN.sort_values(by=['Confirmed'])
    print("Bar - " + str(selected_day))


    df22 = df2.groupby('Country')['Confirmed'].sum()
    df22 = df22.sort_values(ascending=True)
    df22 = df22.reset_index()
    print(df22.head())

    fig = make_subplots(rows=1, cols=2, specs=[[{}, {}]], shared_xaxes=False,
                    shared_yaxes=False, vertical_spacing=0.001)

    fig.append_trace(go.Bar(
        x=df2_CN['Confirmed'],
        y=df2_CN['State'],
        marker=dict(
            color='#fac1b7',
            line=dict(
                color='#fac1b7',
                width=1),
        ),
        name='Inside China by State',
        orientation='h',
    ), 1, 1)

    fig.append_trace(go.Bar(
        x=df22['Confirmed'],
        y=df22['Country'],
        marker=dict(
            color='#92d8d8',
            line=dict(
                color='#92d8d8',
                width=1),
        ),
        name='Outside of China by Country',
        orientation='h',
    ), 1, 2)


    fig.update_layout(
    # title='No of Confirmed by Region',
    yaxis=dict(
        showgrid=False,
        showline=False,
        showticklabels=True,
        domain=[0, 0.85],
    ),
    yaxis2=dict(
        showgrid=False,
        showline=False,
        showticklabels=True ,
        domain=[0, 0.85],
    ),
    xaxis=dict(
        zeroline=False,
        showline=False,
        showticklabels=True,
        showgrid=True,
        domain=[0, 0.42],
    ),
    xaxis2=dict(
        zeroline=False,
        showline=False,
        showticklabels=True,
        showgrid=True,
        domain=[0.47, 1],
    ),
    legend=dict(x=-0.15, y=1, font_size=10),
    margin=dict(l=0, r=0, t=10, b=0, pad=5),
    plot_bgcolor='white',
    )

    annotations = []

    # Adding labels
    for ydn, xd in zip(df2_CN['Confirmed'], df2_CN['State']):
        annotations.append(dict(xref='x1', yref='y1',
                                y=xd, x=ydn + 200,
                                text=ydn,
                                font=dict(family='Arial', size=12,
                                      color='#fac1b7'),
                                showarrow=False))

    for ydn, xd in zip(df22['Confirmed'], df22['Country']):
        annotations.append(dict(xref='x2', yref='y2',
                                y=xd, x=ydn + 0.5,
                                text=ydn,
                                font=dict(family='Arial', size=12,
                                      color='#92d8d8'),
                                showarrow=False))

    fig.update_layout(annotations=annotations)


    return fig


if __name__ == '__main__':
    app.run_server(debug=True)















