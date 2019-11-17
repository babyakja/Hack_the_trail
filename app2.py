import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go
import dash_core_components as dcc
import requests
import chart_studio.plotly as py
import plotly.graph_objs as go
import datetime
import pickle 
from sklearn.ensemble import RandomForestRegressor


def weekend_tag_flask(weekday):
        if weekday == 5 or weekday == 6:
            return 1
        else:
            return 0

def get_daily_max_min(data):

    day_totals = {}
    current_day = ''
    temp_min = 62
    temp_max = 70
    precip = 0 
    for i in data:
        date = i['dt_txt'].split()[0].strip()
        if date != current_day:
            day_totals[date] = [temp_min, temp_max, precip]
            precip = 0 
            current_day = date
            temp_min = i['main']['temp_min']
            temp_max = i['main']['temp_max']
            if 'rain' in i['weather'][0]['description']:
                precip += .1
        else:
            if i['main']['temp_min'] < temp_min:
                temp_min = i['main']['temp_min']
            if i['main']['temp_max'] > temp_max:
                temp_max = i['main']['temp_max']
                
    return day_totals

model = pickle.load(open('./congress_top_trail_model.pkl', 'rb'))

key = '4e6a785a8d5ea2c93c7b01caedb8166e'

forecast_url = "http://api.openweathermap.org/data/2.5/forecast?"

params = {
    'zip':'78701',
    'units':'imperial',
    'appid':key
}

res = requests.get(forecast_url, params)
temp = res.json()['list']

temps = get_daily_max_min(temp)


dct = {}
for k,v in temps.items():
    date = datetime.datetime.strptime(k, '%Y-%m-%d')
    precip = v[2]
    tmin = v[0]
    tmax = v[1]
    is_weekend = weekend_tag_flask(date.weekday())
    base = [0] * 12
    base[date.month - 1] = 1

    dct[k] = [precip, tmax,tmin, tmin*tmax, is_weekend] + base
X = pd.DataFrame(dct).T

predictions = model.predict(X)



external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

        
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
df = pd.read_csv(
    'https://gist.githubusercontent.com/chriddyp/' +
    '5d1ea79569ed194d432e56108a04d188/raw/' +
    'a9f9e8076b837d541398e999dcbac2b2826a81f8/'+
    'gdp-life-exp-2007.csv')
df2 =  pd.read_csv('weather_all_days.csv')
colors = {
    'background': '#111111',
    'text': '#FA861A'
    
}

app.layout = html.Div(children=[

    html.H1(
        children='Traffic Forcasting',
        style={
            'textAlign': 'right',
            'color': '#FA861A',
            'background-image': 'url(https://upload.wikimedia.org/wikipedia/commons/thumb/2/2d/ZilkerBotanicalGarden-Entrance.JPG/1200px-ZilkerBotanicalGarden-Entrance.JPG)',
            'backgroundColor': colors['background'],
            'height': '15%',
            'display': 'block'
        },
    ),
        html.Img(

        src="https://i.ibb.co/BjhrTk1/TTF.png",

        className="lo",

        style={

        'height': '70%',

        'width': '30%',

        'float': 'center',

        'position': 'center',

        'margin-top': 20,

        'margin-right': 20

        },

    ),

    html.Label('Select a Trail'),
    dcc.RadioItems(
        options=[
            {'label': 'Butler Trail : Crenshaw Bridge - Urban Trail', 'value': 'CRENSHAW'},
            {'label': 'Shoal Creek Trail & 24th St- Urban Trail', 'value': 'SHOAL'},
            {'label': 'Butler Trail: South Lamar - Urban Trail', 'value': 'LAMAR'},
            {'label': 'Butler Trail: North Congress - Urban Trail', 'value' : 'CONGRESS'},
            {'label': 'Butler Trail : Longhorn Dam - Urban Trail', 'value': 'LONGHORN'}
        ],
        value='MTL'
    ),

    html.Br(),
    html.Div(
        children=[
            html.Div(html.Label('Temperature')),
            html.Div(
            html.Div(                
    dcc.RangeSlider(
        id='temp-range-slider',
        min=10,
        max=120,
        step=1,
        marks={20: '20 °F',
        40: '40 °F',
        60: '60 °F',
        80: '80 °F',
        100: '100 °F',
        120: '120 °F'},
        value=[10,120]
    ), style={'display': 'block', 'width': '28%'})
    ),
    html.Br(),
    html.Br(),
    html.Div(id='output-container-range-slider')
        ]
    ),
    

    # html.Div(id='output-container-range-slider'),
html.Br(),
html.Br(),
    html.Div(children=dcc.Graph(
        id='traffic-date',
        figure={
            'data': [
                go.Scatter(
                    y=predictions,
                    x=X.index,
                    #text=df[df['continent'] == i]['country'],
                    mode='lines',
                    opacity=0.7,
                    marker={
                        'size': 15,
                        'line': {'width': 0.5, 'color': 'white'}
                    },
                    name=i
                ) for i in range(1,5)
            ],
            'layout': go.Layout(
                xaxis={'title': 'Day'},
                yaxis={'title': 'Traffic'},
                margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
                legend={'x': 0, 'y': 1},
                hovermode='closest'
            )
        }

    ), style={
        'width' : '75%'
    })
])
@app.callback(
    dash.dependencies.Output('output-container-range-slider', 'children'),
    [dash.dependencies.Input('temp-range-slider', 'value')])
def update_output(value):
    transformed_value = [v for v in value]
    return 'Temperature Range "Min-{}" "Max-{}"'.format(transformed_value[0], transformed_value[1])

@app.callback(
    dash.dependencies.Output('traffic-date', 'figure'),
    [dash.dependencies.Input('temp-range-slider', 'value')])
def update_graph(value):
    temp_value = [v for v in value]
    dff = df2[df2['TMIN'] >= temp_value[0]]
    dff = dff[dff['TMAX'] <= temp_value[1]]

    return {
        'data': [
                go.Scatter(
                    y=predictions,
                    x=X.index,
                    mode='lines',
                    opacity=0.8,
                    marker={
                        'size': 25,
                        'line': {'width': 0.5, 'color': 'white'}
                    },
                    name=i
                ) for i in range(0,1)
            ],
            'layout': go.Layout(
                title='Congress Trail Projected Traffic',
                showlegend=True,
                xaxis={'title': 'Day'},
                yaxis={'title': 'Traffic'},
                margin={'l': 40, 'b': 40, 't': 50, 'r': 10},
                legend={'x': 0, 'y': 1},
                hovermode='closest'
            )
    }

if __name__ == '__main__':
    app.run_server(debug=True)
