import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
import plotly.graph_objects as go
import pandas as pd
from dash.dependencies import Input, Output

# Load the dataset
df = pd.read_csv('https://github.com/rmejia41/open_datasets/raw/main/PWS_2016_2023_updated.csv')

# Prepare the data
df_melted = df.melt(id_vars=["State", "Two Letter State"], var_name="Year", value_name="Population")
df_melted['Year'] = pd.to_numeric(df_melted['Year'])

# Initialize Dash app with the Quartz theme
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])
server = app.server

# Define the app layout
app.layout = html.Div([
    html.H1('State Populations on Public Water Systems (2016-2023)',
            style={'textAlign': 'center', 'fontSize': '34px', 'marginBottom': '40px',
                   'fontFamily': 'Roboto, sans-serif', 'color': '#3D85C6'}),
    html.Div([
        # Choropleth map section
        html.Div([
            html.Label('Select Year for Map:', style={'fontFamily': 'Roboto, sans-serif', 'color': '#3D85C6'}),
            dcc.Dropdown(
                id='year-dropdown',
                options=[{'label': year, 'value': year} for year in sorted(df_melted['Year'].unique())],
                value=sorted(df_melted['Year'].unique())[0],
                style={'width': '65%', 'marginBottom': 20}
            ),
            dcc.Graph(id='choropleth-map'),
        ], style={'width': '50%', 'display': 'inline-block', 'paddingRight': '20px'}),

        # Line chart section
        html.Div([
            html.Label('Select States for Line Chart:', style={'fontFamily': 'Roboto, sans-serif', 'color': '#3D85C6'}),
            dcc.Dropdown(
                id='state-dropdown',
                options=[{'label': state, 'value': state} for state in sorted(df['State'].unique())],
                value=[sorted(df['State'].unique())[0]],
                multi=True,
                style={'width': '100%', 'marginBottom': 20}
            ),
            dcc.Graph(id='line-chart'),
        ], style={'width': '50%', 'display': 'inline-block'}),
    ], style={'display': 'flex', 'justifyContent': 'center', 'alignItems': 'flex-start'})
])

@app.callback(
    Output('choropleth-map', 'figure'),
    [Input('year-dropdown', 'value')]
)
def update_map(selected_year):
    df_filtered = df_melted[df_melted['Year'] == selected_year]
    zmin_value = df_filtered['Population'].quantile(0.01)
    zmax_value = df_filtered['Population'].quantile(0.99)

    fig = go.Figure(data=go.Choropleth(
        locations=df_filtered['Two Letter State'],
        z=df_filtered['Population'],
        locationmode='USA-states',
        colorscale='Viridis',
        colorbar_title="Population",
        zmin=zmin_value,
        zmax=zmax_value,
    ))
    fig.update_layout(
        title_text=f'US State Populations on PWS in {selected_year}',
        geo_scope='usa',
    )
    return fig


@app.callback(
    Output('line-chart', 'figure'),
    [Input('state-dropdown', 'value')]
)
def update_line_chart(selected_states):
    fig = go.Figure()
    for state in selected_states:
        df_filtered = df_melted[df_melted['State'] == state]
        fig.add_trace(go.Scatter(
            x=df_filtered['Year'],
            y=df_filtered['Population'],
            mode='lines+markers',
            name=state
        ))

    fig.update_layout(
        title='PWS Population Changes Over Time',
        xaxis_title='Year',
        yaxis_title='Population',
        hovermode='closest'
    )
    return fig

if __name__ == '__main__':
    app.run_server(debug=False, port=8051)