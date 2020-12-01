import plotly.express as px

if __name__ == "__main__":
    df = px.data.gapminder().query("continent == 'Oceania'")
    fig = px.line(df, x='year', y='lifeExp', color='country')
    fig.show()
