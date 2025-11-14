import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import io, base64

from dash import Dash, html, dcc
import plotly.express as px


# ------------------------------
# LOAD DATA
# ------------------------------
dataframe = pd.read_csv("Zomato data .xls")


# ------------------------------
# CLEAN RATE COLUMN
# ------------------------------
def handleRate(value):
    try:
        return float(str(value).split('/')[0])
    except:
        return None

dataframe['rate'] = dataframe['rate'].apply(handleRate)


# ------------------------------
# PIE CHART (Matplotlib)
# ------------------------------
restaurant_type_counts = dataframe['listed_in(type)'].value_counts()

plt.figure(figsize=(8, 8))
plt.pie(
    restaurant_type_counts,
    labels=restaurant_type_counts.index,
    autopct='%1.1f%%',
    colors=sns.color_palette('Set2', len(restaurant_type_counts))
)
plt.title("Restaurant Type Proportions")

buf = io.BytesIO()
plt.savefig(buf, format="png")
buf.seek(0)
pie_chart_img = base64.b64encode(buf.read()).decode("utf-8")
buf.close()


# ------------------------------
# DASH APP
# ------------------------------
app = Dash(__name__)

app.layout = html.Div([
    html.H1("Zomato Data Analysis Dashboard", style={'textAlign': 'center'}),

    dcc.Tabs([
        # TAB 1 – Ratings Distribution
        dcc.Tab(label='Ratings Distribution', children=[
            dcc.Graph(
                figure=px.histogram(
                    dataframe,
                    x='rate',
                    nbins=10,
                    title="Ratings Distribution"
                )
            )
        ]),

        # TAB 2 – Votes by Restaurant Type
        dcc.Tab(label='Votes by Restaurant Type', children=[
            dcc.Graph(
                figure=px.bar(
                    dataframe.groupby('listed_in(type)')['votes'].sum().reset_index(),
                    x='listed_in(type)',
                    y='votes',
                    title="Total Votes by Restaurant Type",
                    color='listed_in(type)'
                )
            )
        ]),

        # TAB 3 – Online Orders vs Ratings
        dcc.Tab(label='Online Orders vs Ratings', children=[
            dcc.Graph(
                figure=px.box(
                    dataframe,
                    x='online_order',
                    y='rate',
                    title="Online Orders vs Ratings",
                    color='online_order'
                )
            )
        ]),

        # TAB 4 – Pie Chart (Matplotlib Output)
        dcc.Tab(label='Restaurant Type Proportion', children=[
            html.Div([
                html.H3("Restaurant Type Proportions"),
                html.Img(src=f"data:image/png;base64,{pie_chart_img}",
                         style={'width': '80%', 'height': 'auto'})
            ])
        ]),

        # TAB 5 – Heatmap
        dcc.Tab(label='Heatmap Analysis', children=[
            dcc.Graph(
                figure=px.imshow(
                    dataframe.pivot_table(
                        index='listed_in(type)',
                        columns='online_order',
                        aggfunc='size',
                        fill_value=0
                    ),
                    title="Heatmap of Online Orders by Type",
                    color_continuous_scale='YlGnBu'
                )
            )
        ])
    ])
])


# ------------------------------
# RUN APP
# ------------------------------
if __name__ == '__main__':
    app.run(debug=True)
