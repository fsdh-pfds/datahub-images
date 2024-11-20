"""
Dash application for celestial bodies database management.

This module provides a web interface for querying, adding, and deleting 
celestial bodies from a PostgreSQL database.
"""

import os
import dash
import pandas as pd
import psycopg2
from dash import dcc, html
from dash.dependencies import Input, Output, State
from dotenv import load_dotenv


ERROR_OCCUR = False

load_dotenv()  # Load environment variables from .env file

try:
    # Retrieve the secrets containing DB connection details from environment variables
    DB_NAME = os.getenv("DB_NAME", "YourDB")
    DB_HOST = os.getenv("DB_HOST", "postgres.database.azure.com")
    DB_USER = os.getenv("DB_USER", "user")
    # It will default to an empty string if not set
    DB_PASS = os.getenv("DB_PASS", "")

    print(f"DB_HOST is {DB_HOST}")
except Exception as e:
    ERROR_OCCUR = True
    print(f"An error occurred: {e}")


# Define the layout of the app
app = dash.Dash(
    __name__,
    requests_pathname_prefix="/app/SCAWWAS/",
    routes_pathname_prefix="/app/SCAWWAS/",
)

app.layout = html.Div(
    [
        html.H1(
            "Sample FSDH Dash Application | Exemple d'une application Dash sur le DHSF"
        ),
        # Form 1 - Query database
        html.H2(
            "Celestial Body Database Query | Requête de la base de données des corps célestes"
        ),
        html.P(
            "The database contains information about celestial bodies. "
            "Enter the name of a celestial body to query the database. "
            "| La base de données contient des informations sur les corps célestes. "
            "Entrez le nom d'un corps céleste pour interroger la base de données."
        ),
        dcc.Input(
            id="query-name",
            type="text",
            placeholder="Celestial body name | Nom du corps céleste",
        ),
        html.Button(
            "Query Database | Interroger la base de données",
            id="query-button",
            n_clicks=0,
        ),
        html.Div(id="query-output"),
        # Figure 1 - Plot celestial bodies
        html.H3("Celestial Bodies Plot | Tracé des corps célestes"),
        html.P(
            "The plot shows the mass of celestial bodies against their distance from the sun. "
            "| Le graphique montre la masse des corps célestes par rapport à leur distance par rapport au soleil."
        ),
        dcc.Graph(id="celestial-bodies-plot"),
        # Form 2 - Add new celestial body
        html.H1("Add New Celestial Body | Ajouter un nouveau corps céleste"),
        html.P(
            "Add a new celestial body to the database. "
            "| Ajoutez un nouveau corps céleste à la base de données."
        ),
        dcc.Input(id="add-name", type="text", placeholder="Name | Nom"),
        dcc.Input(id="add-body-type", type="text", placeholder="Type | Type"),
        dcc.Input(id="add-radius", type="number", placeholder="Radius | Rayon"),
        dcc.Input(id="add-mass", type="number", placeholder="Mass | Masse"),
        dcc.Input(
            id="add-distance",
            type="number",
            placeholder="Distance from sun | Distance par rapport au soleil",
        ),
        html.Button(
            "Add Celestial Body | Ajouter un corps céleste", id="add-button", n_clicks=0
        ),
        html.Div(id="add-output"),
        # Form 3 - Delete celestial body by ID
        html.H1("Delete Celestial Body | Supprimer un corps céleste"),
        html.P(
            "Delete a celestial body from the database by ID. "
            "| Supprimez un corps céleste de la base de données par ID."
        ),
        dcc.Input(id="delete-id", type="number", placeholder="ID"),
        html.Button(
            "Delete Celestial Body | Supprimer un corps céleste",
            id="delete-button",
            n_clicks=0,
        ),
        html.Div(id="delete-output"),
    ],
    style={"width": "50%", "margin": "auto", "font-family": "Arial, sans-serif"},
)


@app.callback(
    Output("delete-output", "children"),
    [Input("delete-button", "n_clicks")],
    [State("delete-id", "value")],
)
def delete_celestial_body(n_clicks, body_id):
    """
    Delete a celestial body from the database based on its ID.

    Args:
        n_clicks (int): Number of times the delete button has been clicked.
        body_id (int): ID of the celestial body to be deleted.

    Returns:
        str: Confirmation message or empty string.
    """
    if n_clicks > 0:
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(
            dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST
        )

        # Create a new cursor
        cur = conn.cursor()

        # Run the query
        cur.execute("DELETE FROM celestial_bodies WHERE id = %s", (body_id,))
        conn.commit()

        # Close the cursor and connection to the database
        cur.close()
        conn.close()

        return "Celestial body deleted successfully."
    return ""


@app.callback(
    Output("celestial-bodies-plot", "figure"),
    [Input("query-button", "n_clicks")],
    [State("query-name", "value")],
)
def plot_celestial_bodies(n_clicks, name):
    """
    Generate a scatter plot of celestial bodies matching the given name.

    Args:
        n_clicks (int): Number of times the query button has been clicked.
        name (str): Name or partial name of celestial bodies to plot.

    Returns:
        dict: Plotly figure configuration or empty dictionary.
    """
    if n_clicks > 0:
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(
            dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST
        )

        # Create a new cursor
        cur = conn.cursor()

        # Run the query
        cur.execute(f"SELECT * FROM celestial_bodies WHERE name LIKE '%{name}%'")
        result = cur.fetchall()

        # Close the cursor and connection to the database
        cur.close()
        conn.close()

        # Convert query result to DataFrame
        df = pd.DataFrame(
            result,
            columns=["id", "name", "type", "radius", "mass", "distance from sun"],
        )

        # Create a scatter plot
        fig = {
            "data": [
                {
                    "x": df["distance from sun"],
                    "y": df["mass"],
                    "text": df["name"],
                    "mode": "markers",
                }
            ],
            "layout": {
                "title": "Celestial Bodies",
                "xaxis": {"title": "Distance from sun (km)"},
                "yaxis": {"title": "Mass (kg)"},
            },
        }

        return fig
    return {}


@app.callback(
    Output("add-output", "children"),
    [Input("add-button", "n_clicks")],
    [
        State("add-name", "value"),
        State("add-type", "value"),
        State("add-radius", "value"),
        State("add-mass", "value"),
        State("add-distance", "value"),
    ],
)
def add_celestial_body(
    n_clicks, name, type, radius, mass, distance
):
    """
    Add a new celestial body to the database.

    Args:
        n_clicks (int): Number of times the add button has been clicked.
        name (str): Name of the celestial body.
        body_type (str): Type of the celestial body.
        radius (float): Mean radius of the celestial body.
        mass (float): Mass of the celestial body.
        distance (float): Distance from the sun.

    Returns:
        str: Confirmation message or empty string.
    """
    if n_clicks > 0:
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(
            dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST
        )

        # Create a new cursor
        cur = conn.cursor()

        # Run the query
        query = (
            "INSERT INTO celestial_bodies "
            "(name, body_type, mean_radius_km, mass_kg, distance_from_sun_km) "
            "VALUES (%s, %s, %s, %s, %s)"
        )
        cur.execute(
            query,
            (name, body_type, radius, mass, distance),
        )
        conn.commit()

        # Close the cursor and connection to the database
        cur.close()
        conn.close()

        return "Celestial body added successfully."
    return ""


@app.callback(
    Output("query-output", "children"),
    [Input("query-button", "n_clicks")],
    [State("query-name", "value")],
)
def get_celestial_body(n_clicks, name):
    """
    Retrieve celestial bodies matching the given name.

    Args:
        n_clicks (int): Number of times the query button has been clicked.
        name (str): Name or partial name of celestial bodies to query.

    Returns:
        Union[html.Table, str]: Table of query results or message.
    """
    if n_clicks > 0:
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(
            dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST
        )

        # Create a new cursor
        cur = conn.cursor()

        # Run the query
        cur.execute(f"SELECT * FROM celestial_bodies WHERE name LIKE '%{name}%'")
        result = cur.fetchall()

        # Close the cursor and connection to the database
        cur.close()
        conn.close()

        # Convert query result to DataFrame, then to a HTML table
        if result:
            df = pd.DataFrame(
                result,
                columns=["id", "name", "type", "radius", "mass", "distance from sun"],
            )
            return html.Table(
                # Header
                [
                    html.Tr(
                        [
                            html.Th(
                                col,
                                style={"border": "1px solid black", "padding": "8px"},
                            )
                            for col in df.columns
                        ]
                    )
                ]
                +
                # Body
                [
                    html.Tr(
                        [
                            html.Td(
                                df.iloc[i][col],
                                style={"border": "1px solid black", "padding": "8px"},
                            )
                            for col in df.columns
                        ]
                    )
                    for i in range(len(df))
                ]
            )
        return "No celestial bodies found with that name."
    return ""


# Run the app
if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port=80)