from multiprocessing import set_forkserver_preload
from click import option
import streamlit as st
import pandas as pd
from datetime import datetime
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import altair as alt
import plotly.express as px
import requests
st.set_page_config(layout='wide')
# removing Altair options menu
st.markdown("""
    <style type='text/css'>
        details {
            display: none;
        }
    </style>
""", unsafe_allow_html=True)


# creating containers
header = st.container()
dataset = st.container()
visualization = st.container()
world_map = st.container()

# importing data


@st.cache
def nyt_data():

    df = pd.read_csv("nyt_sentiment.csv", parse_dates=[
                     "date"], index_col=["date"])

    return df


# header
with header:
    st.title(
        "NYT News Sentiment Analysis")
    st.markdown(
        "![NYT](https://developer.nytimes.com/files/poweredby_nytimes_200a.png?v=1583354208344)")

    st.header("Project Background")
    st.markdown("In a fast paced society being able to share information as fast as possible is key. Data science comes in aid trying to process these informations and return them back in a usable and readeable way. To me, one of the most interesting applications for Data Science is the one that involves text analysis and Natural Language Processing (NLP). There are numerous books and publications about this subject and it's not hard to understand why: being able to make a computer process and understand human language is fascinating and nevertheless challenging. ")
    st.markdown("Having the possibility to evaluate in a blink of an eye what a time period has been characterized of by analyzing news is the point of focus of this study - condensing them in few graphs or charts giving simple answers to more complex data. In my opinion it is interesting to let a machine elaborate some refined data to have insights and outcomes on a certain period based on news and articles.")
    link = "This web app is an extract of [NYT News Analysis](https://github.com/massigarg/NYT-news-analysis) study, where we will consider headlines sentiment scores filtered by geographic subsection. We will have a look on how this score changed in time and how positive and negative headlines are distribuited for each continent."
    st.markdown(link, unsafe_allow_html=True)


with dataset:
    st.subheader("NYT Dataframe")
    st.markdown("Columns collected from NYT API are 'Headline', 'Date' and 'Subsection' while 'Sentiment' has been processed using nltk sentimet module and then binned in the 'Sentiment_bin' column. Please note how, even if the use of world zones subsection dates back to 1982, it has been used consistently only after years 2000s. Thus this analysis will comprehend date only between 2000 and 2022")

    st.write(nyt_data().set_index(nyt_data().index.date))


with visualization:
    col1, col2 = st.columns([1, 1])
    # continent choice
    with col1:
        options = st.multiselect(
            'Choose Continent',
            [
                'Europe',
                'Africa',
                'North America',
                'South America',
                "Asia",
                "Australia",
            ],
            [
                'Europe',
                'Africa',
                'North America',
                'South America',
                "Asia",
                "Australia",
            ])

    # date choice
    with col2:

        range_dates = st.slider(
            "Choose Date:",
            value=(datetime(1982, 1, 1), datetime(2022, 1, 1)),
            format="YYYY")

        mask = (nyt_data().index.date > range_dates[0].date()) & (
            nyt_data().index.date <= range_dates[1].date())

    st.subheader(
        f"Scores between {range_dates[0].year} - {range_dates[1].year}")

    col1, col2 = st.columns([1, 1])

    # adjusted df for altair vizualization
    res_vader = (nyt_data().loc[mask].groupby(["sentiment_bin", "subsection"])["headline"]
                 .count()
                 .reset_index()
                 .rename(columns={"headline": "count"})
                 )
    # hist visualization
    with col1:
        hist_vader = alt.Chart(res_vader[res_vader["subsection"].isin(options)], title="Sentiment Score Distribution").mark_bar(width=15).encode(
            alt.X("sentiment_bin:Q", axis=alt.Axis(title="")),
            y=alt.Y('count:Q', axis=alt.Axis(title="")),
            color=alt.Color('sentiment_bin:Q',
                            scale=alt.Scale(scheme='redyellowgreen'),
                            legend=alt.Legend(title="Score")),
            tooltip=['sentiment_bin', 'count']
        ).properties(height=450)

        st.altair_chart(hist_vader, use_container_width=True)

    with col2:

        stacked_bar = alt.Chart(res_vader[res_vader["subsection"].isin(options)], title="Continent Sentiment Score").mark_bar().encode(
            y=alt.X("subsection", axis=alt.Axis(title="")),
            x=alt.Y('count:Q', stack='normalize',
                    axis=alt.Axis(title="", labels=False)),
            color=alt.Color('sentiment_bin',
                            scale=alt.Scale(
                                scheme='redyellowgreen'),
                            legend=alt.Legend(title="Score")),
            tooltip=['sentiment_bin', 'subsection', 'count'],
            order=alt.Order(
                # Sort the segments of the bars by this field
                'sentiment_bin',
                sort='ascending')
        ).properties(height=450)

        st.altair_chart(stacked_bar, use_container_width=True)


with world_map:

    continents = requests.get(
        "https://gist.githubusercontent.com/hrbrmstr/91ea5cc9474286c72838/raw/59421ff9b268ff0929b051ddafafbeb94a4c1910/continents.json"
    ).json()

    # creating a continents df
    continents_df = nyt_data().loc[mask].groupby("subsection")[
        "sentiment"].mean().reset_index()
    continents_df.rename(columns={"subsection": "CONTINENT"}, inplace=True)

    continents_df = continents_df.round(decimals=2)

    fig = px.choropleth_mapbox(continents_df[continents_df["CONTINENT"].isin(options)], geojson=continents, locations='CONTINENT', featureidkey="properties.CONTINENT",
                               color='sentiment',
                               color_continuous_scale="RdYlBu",
                               mapbox_style="carto-darkmatter",
                               hover_data=["sentiment"],
                               labels={
                                   "sentiment": "Sentiment Score",
    },
        zoom=1,
        opacity=0.5,
    )
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

    st.plotly_chart(fig, use_container_width=True)
    st.caption(
        f"World Plot: sentiment mean value between {range_dates[0].year} and {range_dates[1].year}")
