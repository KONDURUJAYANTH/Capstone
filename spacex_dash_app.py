# Import required libraries
import pandas as pd
from dash import dcc, html, Dash, Input, Output
import plotly.express as px

# Read the SpaceX launch data into a pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")

# Minimum and maximum payload for the slider
min_payload = spacex_df['Payload Mass (kg)'].min()
max_payload = spacex_df['Payload Mass (kg)'].max()

# Launch site options for dropdown
site_options = [{'label': 'All Sites', 'value': 'ALL'}]
site_options += [{'label': site, 'value': site} for site in spacex_df['Launch Site'].unique()]

# Create a Dash application
app = Dash(__name__)

# App layout
app.layout = html.Div([
    html.H1(
        'SpaceX Launch Records Dashboard',
        style={'textAlign': 'center', 'color': '#503D36', 'font-size': '40px'}
    ),
    # Dropdown for selecting launch site
    dcc.Dropdown(
        id='site-dropdown',
        options=site_options,
        value='ALL',
        placeholder="Select a Launch Site here",
        searchable=True,
        style={'width': '100%', 'padding': '3px', 'font-size': '20px', 'textAlign': 'left', 'margin': 'auto'}
    ),
    html.Br(),
    # Pie chart for success rate
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),
    # Payload range slider
    html.P("Payload range (Kg):", style={'font-size': '20px'}),
    dcc.RangeSlider(
        id='payload-slider',
        min=min_payload,
        max=max_payload,
        step=1000,
        marks={int(i): f'{int(i)}' for i in range(int(min_payload), int(max_payload) + 1, 1000)},
        value=[min_payload, max_payload],
        tooltip={"placement": "bottom", "always_visible": True}
    ),
    html.Br(),
    # Scatter plot for payload vs success
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# Callback for updating the pie chart
@app.callback(
    Output('success-pie-chart', 'figure'),
    [Input('site-dropdown', 'value')]
)
def update_pie_chart(selected_site):
    if selected_site == 'ALL':
        # Pie chart showing success counts across all sites
        fig = px.pie(
            spacex_df,
            values='class',
            names='Launch Site',
            title='Total Success Launches By Site'
        )
    else:
        # Filter data for the selected site
        filtered_df = spacex_df[spacex_df['Launch Site'] == selected_site]
        # Compute success and failure counts
        success_counts = filtered_df['class'].value_counts()
        fig = px.pie(
            values=success_counts,
            names=success_counts.index,
            title=f'Total Success Launches for site {selected_site}'
        )
    return fig

# Callback for updating the scatter plot
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [Input('site-dropdown', 'value'),
     Input('payload-slider', 'value')]
)
def update_scatter_chart(selected_site, payload_range):
    # Filter data based on payload range
    low, high = payload_range
    filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= low) & (spacex_df['Payload Mass (kg)'] <= high)]
    
    if selected_site == 'ALL':
        # Scatter plot for all sites
        fig = px.scatter(
            filtered_df,
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version Category',
            title='Correlation between Payload and Success for all Sites',
            labels={'class': 'Launch Outcome'}
        )
    else:
        # Scatter plot for selected site
        filtered_df = filtered_df[filtered_df['Launch Site'] == selected_site]
        fig = px.scatter(
            filtered_df,
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version Category',
            title=f'Correlation between Payload and Success for site {selected_site}',
            labels={'class': 'Launch Outcome'}
        )
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
