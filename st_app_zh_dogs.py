# necessary packages
import streamlit as st
import pandas as pd
import plotly.express as px
import json
from copy import deepcopy

# loda data

@st.cache_data
def load_data(path):
    df = pd.read_csv(path)
    return df

df_dogs = load_data("data/processed/zurich_dogs.csv")
df_districts = load_data("data/processed/district_info.csv")

with open("data/raw/stzh.adm_stadtkreise_a.json") as jsonfile:
    geo_district = json.load(jsonfile)

# The title
st.title("Dogs of Zürich")

# Description
st.write("This app is intended to give users an interface where they can explore the data on the dogs of Zürich.")

# Section header
st.header("Dogs on the map")

# Description
st.write("Here you can select the information that you want to display, and for which dog breed. Please note that dog breeds are limited to the most popular 20 categories.")

# Selecting dog breeds and main info to display
left_column, right_column = st.columns(2)

display_info = left_column.radio(
    label = "Please select the information you want to display", 
    options = ["Total number of dogs", 
               "Dog number per 1000 people", 
               "Average age of dogs"] 
)

breeds_list = ["All"] + df_dogs.value_counts("dog_breed")[:20].index.to_list()

breed_select = right_column.selectbox(
    label = "Please choose a dog breed", 
    options = breeds_list
)

# control flows to define the subset

if breed_select == "All": 
    df_subset = df_dogs
else:
    df_subset = df_dogs[df_dogs["dog_breed"] == breed_select]

# calculate statistics to display and store in a df

if display_info == "Average age of dogs": 
    dog_age = df_subset.groupby("district")["dog_age"].mean()
    df_stats = pd.DataFrame(dog_age).reset_index().rename(columns = {"dog_age" : "resp_var"})
elif display_info == "Total number of dogs":
    dog_count = df_subset.value_counts("district")
    df_stats = pd.DataFrame(dog_count).sort_index().reset_index().rename(columns = {0 : "resp_var"})
elif display_info == "Dog number per 1000 people":
    dog_count = df_subset.value_counts("district")
    df_stats = pd.DataFrame(dog_count).sort_index().reset_index().rename(columns = {0 : "num_dogs"})
    df_stats = df_stats.merge(df_districts, on = "district")
    df_stats["resp_var"] = (df_stats["num_dogs"] / df_stats["pop"]) * 1000

# label the districts in a new column
df_stats["district_name"] = df_stats["district"].map({
    1 : "Altstadt", 
    2 : "Wollishofen, Leimbach, Enge", 
    3 : "Wiedikon", 
    4 : "Aussersihl", 
    5 : "Industriequartier", 
    6 : "Unterstrass, Oberstrass", 
    7 : "Funtern, Hottingen, Hirslanden, Witikon", 
    8 : "Riesbach", 
    9 : "Albisriesen, Altstetten", 
    10 : "Hoengg, Wipkingen", 
    11 : "Affoltern, Seebach, Oerlikon", 
    12 : "Schwamendingen"
})

# whether or not decimals will be displayed

if display_info == "Average age of dogs": 
    num_prec = ":.2f"
elif display_info == "Total number of dogs":
    num_prec = True
elif display_info == "Dog number per 1000 people":
    num_prec = ":.2f"

# create map with the stats df

fig_map = px.choropleth_mapbox(
    df_stats, 
    geojson = geo_district, 
    featureidkey = "properties.name",
    locations = "district", 
    color = "resp_var", 
    color_continuous_scale = px.colors.sequential.Viridis,
    opacity=0.75,
    mapbox_style="carto-positron", 
    center={"lat": 47.37, "lon": 8.54}, 
    zoom = 10.9, 
    labels = {
        "resp_var" : display_info, 
        "district_name" : "District"
    }, 
    hover_data = {
        "district" : False, 
        "district_name" : True, 
        "resp_var" : num_prec
    }
)

fig_map.update_layout(
    margin={"r":0,"t":40,"l":0,"b":0}, 
    autosize = False, 
    width = 1000, 
    height = 600, 
    title_text = f"{display_info} by district in Zürich. Breed: {breed_select}"
)

st.plotly_chart(fig_map)