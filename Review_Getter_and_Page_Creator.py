import streamlit as st
import streamlit.components.v1 as components
import plotly.graph_objects as go
import requests
import json
import algo
import pandas as pd

baseURL = 'https://imdb-api.com/en/API'
apiKey = 'k_pqqtwryw'
getEmoji = {
    "happy": "😊",
    "neutral": "😐",
    "sad": "😔",
    "disgust": "🤢",
    "surprise": "😲",
    "fear": "😨",
    "angry": "😡",
    "positive": "🙂",
    "neutral": "😐",
    "negative": "☹️",
}


def plotPie(labels, values):
    if len(values)>0:
        fig = go.Figure(
        go.Pie(
            labels=labels,
            values=[value * 100 for value in values],
            hoverinfo="label+percent",
            textinfo="value"
        ))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.write("No Reviews Found")

lastSearched = ""
cacheData = {}


def getMovies(movieName):
    response = requests.get('{baseURL}/SearchMovie/{apiKey}/{movieName}'.format(baseURL=baseURL, apiKey=apiKey, movieName=movieName))
    response = response.json()
        # st.write(i)
    if (isinstance(response["results"], list)):
        movies = [{"id": result['id'], "title": result['title'], "image": result["image"],
                   "description": result["description"]} for result in response["results"]]
        return movies
    else:
        # st.error("No Such Movie Found")
        return []


def getFirst200Words(string):
    if len(string) > 200:
        return string[:200]
    return string


def getReviews(id):
    res = requests.get('{baseURL}/Reviews/{apiKey}/{id}'.format(baseURL=baseURL, apiKey=apiKey, id=id))
    res = res.json()

    if (res["errorMessage"] != ""):
        # st.error(res["errorMessage"])
        return []
    items = res["items"]
    if len(items) > 20:
        items = items[0:20]
    reviews = [getFirst200Words(item["title"] + " " + item["content"]) for item in items]
    return reviews


def getData(movieName):
    print("Sending request to get movies!!!!!!")
    movies = getMovies(movieName)
    data = []
    if(len(movies) == 1):
        pass
    else:
        st.write('Please Wait, We are fetching dataset for all Related Movies & Running reviews through the Data Model')
    for movie in movies:
        reviews = getReviews(movie["id"])
        data.append(
            {"title": movie["title"], "image": movie["image"], "description": movie["description"], "reviews": reviews})
    return json.dumps({"userSearch": movieName, "result": data})


def displayMovieContent(movie):
    try:
        col1, col2 = st.columns([2, 3])
        with col1:
            st.image(movie["image"], width=200)
        with col2:
            st.components.v1.html("""
                                <h3 style="color: #1e293b; font-family: Source Sans Pro, sans-serif; font-size: 20px; margin-bottom: 10px; margin-top: 60px;">{}</h3>
                                <p style="color: #64748b; font-family: Source Sans Pro, sans-serif; font-size: 14px;">{}</p>
                                """.format(movie["title"], movie["description"]), height=150)
    except :
        pass


def getEmojiString(head):
    emojiHead = ""
    emotions = head.split("-")
    for emotion in emotions:
        emo = emotion.strip()
        emojiHead += getEmoji[emo.lower()]
    return head + " " + emojiHead


def process(movieName, packageName):
    global lastSearched, cacheData
    if (lastSearched != movieName):
        data = getData(movieName)
        lastSearched = movieName
        cacheData = data

    else:
        data = cacheData
    if len(data) > 0:
        st.text("")
        st.components.v1.html("""
                                <h3 style="color: #ef4444; font-family: Source Sans Pro, sans-serif; font-size: 22px; margin-bottom: 0px; margin-top: 40px;">API Response</h3>
                                <p style="color: #57534e; font-family: Source Sans Pro, sans-serif; font-size: 14px;">Expand below to see the API response received for the search</p>
                                """, height=100)
        with st.expander("See JSON Response"):
            with st.container():
                st.json(data)

        # Showcasing result
        st.components.v1.html("""
                                <h3 style="color: #0ea5e9; font-family: Source Sans Pro, sans-serif; font-size: 26px; margin-bottom: 10px; margin-top: 60px;">Result</h3>
                                <p style="color: #57534e; font-family: Source Sans Pro, sans-serif; font-size: 16px;">Below are the movies we received related to your search. We have analyzed each and every one for you. Enjoy!</p>
                                """, height=150)

        for movie in list(json.loads(data)["result"]):
            with st.expander(movie["title"]):
                with st.container():
                    result = applyModal(movie, packageName)
                    keys = list(result.keys())
                    values = list(result.values())
                    st.write("")
                    st.write("")
                    displayMovieContent(movie)
                    for i in range(0, len(keys), 4):
                        if ((i + 3) < len(keys)):

                            cols = st.columns(4)
                            cols[0].metric(getEmojiString(keys[i]), round(values[i], 2), None)
                            cols[1].metric(getEmojiString(keys[i + 1]), round(values[i + 1], 2), None)
                            cols[2].metric(getEmojiString(keys[i + 2]), round(values[i + 2], 2), None)
                            cols[3].metric(getEmojiString(keys[i + 3]), round(values[i + 3], 2), None)
                        else:
                            cols = st.columns(4)
                            for j in range(len(keys) - i):
                                print("Range Values : ", j, len(keys))
                                cols[j].metric(getEmojiString(keys[i + j]), round(values[i + j], 2), None)

                    col1, col2 = st.columns([3, 1])
                    st.write("")
                    st.write("")
                    with col1:
                        st.subheader("Visual Representation")
                        plotPie(list(result.keys()), [value / len(movie["reviews"]) for value in list(result.values())])


def applyModal(movie, packageName):
    if (packageName == "Vader"):
        predictionList = [algo.vader(review) for review in movie["reviews"]]
        valueCounts = dict(pd.Series(predictionList).value_counts())
        print(valueCounts)
        return valueCounts
    else:
        return ""


def renderPage():
    st.title("IMDB Movie Reviews analysis")
    st.text("")
    movieName = st.text_input(' ', placeholder='Enter A Movie Name')
    packageName = 'Vader'
    if st.button('Analyze'):
        if movieName:
            process(movieName, packageName)
