import pandas as pd
import lxml
import plotly.express as px
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output


app = dash.Dash(__name__)
server = app.server
url = 'https://it.wikipedia.org/wiki/Ballando_con_le_stelle_(quindicesima_edizione)'
dfs = pd.read_html(url,
                   attrs={"class": "wikitable"},
                   header=0)
dfs.extend(pd.read_html(url,
                   attrs={"class": "wikitable plainrowheaders"},
                   header=0))

voti = [x for x in dfs if ('Ordine di uscita' in x.columns) and ('Esito' not in x.columns) and ('Punti bonus' in x.columns)]
for i in range(len(voti)):
    new_header = voti[i].iloc[0] #grab the first row for the header
    voti[i] = voti[i][1:] #take the data less the header row
    voti[i].columns = new_header #set the header row as the df header
    voti[i]['puntata'] = i+1
    voti[i]['Concorrenti'] = voti[i]['Concorrenti'].str.replace(r'\[\d+\]', '')
    voti[i]['Concorrenti'] = voti[i]['Concorrenti'].str.replace(r'Samuel Peron', 'Marco De Angelis')

col_options = [dict(label = x, value =x) for x in sorted(voti[0]['Concorrenti'].unique()) if voti]


app.layout = html.Div(children=[
    html.H1("Ballando con le stelle",style={'color': 'gold', 'fontSize': 14}),
    dcc.Dropdown(id = "Concorrenti", value = sorted(voti[0]['Concorrenti'].unique())[0],options = col_options, searchable=False),
    dcc.Graph(id="graph", figure= {})
])

@app.callback(Output('graph','figure'),
             [Input('Concorrenti','value')])

def cb(Concorrenti):
    for i in range(len(voti)):
        first_epis_votes = voti[i]
        if i==0:
            final =(first_epis_votes[first_epis_votes['Concorrenti']==Concorrenti])
        else:
            final =  pd.concat([final,(first_epis_votes[first_epis_votes['Concorrenti']==Concorrenti])])


    final = final.astype({'Zazzaroni': 'int32','Canino': 'int32','Smith': 'int32','Lucarelli': 'int32','Mariotto': 'int32'})
    #final['puntata']=range(1,(final.shape[0]+1))
    df = final #px.data.gapminder()#Dataset
    Concorrenti = Concorrenti if Concorrenti else sorted(voti[0]['Concorrenti'].unique())[0]
    df_year = df.query("Concorrenti == @Concorrenti")
    fig = px.line(df_year, x="puntata", y=['Zazzaroni','Canino','Smith','Lucarelli','Mariotto'],
                  title=Concorrenti,labels={
                     "puntata": "Puntata",
                     "value": "Punteggio",
                      "variable":"Giudice"
                 },
                 color_discrete_map={ # replaces default color mapping by value
                "Zazzaroni": "Black", "Canino": "MediumPurple", "Canino": "MediumPurple", 'Smith':'Red','Lucarelli':'HotPink','Mariotto':'YellowGreen'
            })
    fig.update_layout(#template="simple_white",
                      yaxis=dict(range=[-0.05,10.5]),xaxis=dict(range=[0.98,9.02]))

    fig.update_traces(mode="markers+lines")
    fig.update_layout(autosize=True,

    hoverlabel=dict(
        bgcolor="DarkRed",
        font_size=16,
        font_family="Rockwell"
    )
)
    #fig.write_html("ballandoconlestelle.html")
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
