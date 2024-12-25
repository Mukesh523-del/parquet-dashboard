import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import os

# Load the Parquet file
def load_data(file_path):
    return pd.read_parquet(file_path)

# Initialize the Dash app
app = dash.Dash(__name__)

# Adjust file path to locate the file in the current folder
file_path = os.path.join(os.path.dirname(__file__), "ICE_01_06_17__9_45_group_Zeit  1 - Standardmessrate.parquet")
data = load_data(file_path)

# Layout of the dashboard
app.layout = html.Div([
    html.H1("Parquet File Dashboard", style={"textAlign": "center"}),

    html.Div([
        html.Label("Select Columns for Statistics:"),
        dcc.Dropdown(
            id="column-selector",
            options=[{"label": col, "value": col} for col in data.columns],
            multi=True
        ),
    ]),

    html.Div([
        html.Label("Statistical Measure:"),
        dcc.RadioItems(
            id="stat-selector",
            options=[
                {"label": "Mean", "value": "mean"},
                {"label": "Variance", "value": "var"},
                {"label": "Mode", "value": "mode"}
            ],
            value="mean"
        )
    ]),

    html.Div(id="stat-output", style={"marginTop": 20}),

    html.Div([
        html.Label("Select Columns to Display Values:"),
        dcc.Dropdown(
            id="value-column-selector",
            options=[{"label": col, "value": col} for col in data.columns],
            multi=True
        ),
    ]),

    html.Div(id="value-output", style={"marginTop": 20}),

    html.Div([
        dcc.Graph(id="data-plot")
    ])
])

# Callback for updating statistical output
@app.callback(
    Output("stat-output", "children"),
    [Input("column-selector", "value"),
     Input("stat-selector", "value")]
)
def update_statistics(selected_columns, stat):
    if not selected_columns:
        return "Select columns to calculate statistics."

    stats_result = {}
    for col in selected_columns:
        if data[col].dtype in ["float64", "int64"]:  # Numeric columns only
            if stat == "mean":
                stats_result[col] = data[col].mean()
            elif stat == "var":
                stats_result[col] = data[col].var()
            elif stat == "mode":
                stats_result[col] = data[col].mode().iloc[0]

    return html.Div([
        html.H4("Statistics"),
        html.Ul([html.Li(f"{col}: {value}") for col, value in stats_result.items()])
    ])

# Callback for displaying values in selected columns
@app.callback(
    Output("value-output", "children"),
    [Input("value-column-selector", "value")]
)
def display_values(selected_columns):
    if not selected_columns:
        return "Select columns to display their values."

    values_result = {}
    for col in selected_columns:
        values_result[col] = data[col].unique()

    return html.Div([
        html.H4("Column Values"),
        html.Ul([html.Li(f"{col}: {list(values_result[col])}") for col in values_result])
    ])

# Callback for updating plot
@app.callback(
    Output("data-plot", "figure"),
    [Input("column-selector", "value")]
)
def update_plot(selected_columns):
    if not selected_columns or len(selected_columns) < 2:
        return px.scatter(title="Select at least two columns to display a plot.")

    return px.scatter(data, x=selected_columns[0], y=selected_columns[1], title="Scatter Plot")

# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)
