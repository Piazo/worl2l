import streamlit as st
import pandas as pd
import random
import numpy as np
from PIL import Image
import geopandas
import geoplot
import matplotlib.pyplot as plt

st.set_page_config(page_title="Wordl2l", page_icon=":earth_asia:" ,layout="wide")
df = pd.read_csv("./data/CountryData.csv")

print(df)

world = geopandas.read_file(geopandas.datasets.get_path('naturalearth_lowres'))
if 'pick_new_country' not in st.session_state:
    st.session_state['pick_new_country'] = True
if 'choice_list' not in st.session_state:
    st.session_state['choice_list'] = []
if 'reset_game' not in st.session_state:
    st.session_state['reset_game'] = False

def reset_game():
    st.session_state.pick_new_country = True
    st.session_state.choice_list = []
    st.session_state.reset_game = False


def reset():
    st.session_state.countrySelected = ''




def get_country_list(df):
    return sorted(df["Country"].to_list())



def get_random_country(df):
    return random.choice(df["Country"].to_list())


def get_geom_data_from_name(name):
    return world.query('name == "{}"'.format(name))

def get_country_data_from_name(name):
    return  df[df['Country'] == name]


def display_country(countryName):
    col21, col22, col23 = st.columns([1,4,1])
    countryCode = get_country_data_from_name(countryName)["Abbreviation"].to_list()[0]
    with col22:
        st.image(Image.open('./data/allShapes/'+countryCode.lower()+'.png'))


def get_distance(country1, country2):
    # Reset the indices of the GeoDataFrames
    country1 = country1.reset_index(drop=True)
    country2 = country2.reset_index(drop=True)

    # Reproject the geometries to a projected CRS (EPSG:3857)
    country1 = country1.to_crs('EPSG:3857')
    country2 = country2.to_crs('EPSG:3857')

    # Calculate the centroids of the countries
    country1_centroid = country1['geometry'].centroid
    country2_centroid = country2['geometry'].centroid

    # Calculate the distance between the centroids
    distance_meters = country1_centroid.distance(country2_centroid)

    return int(distance_meters / 1000)


def get_orientation(country1, country2):
    # Reset the indices of the GeoDataFrames
    country1 = country1.reset_index(drop=True)
    country2 = country2.reset_index(drop=True)

    # Reproject the geometries to a projected CRS (EPSG:3857)
    country1 = country1.to_crs('EPSG:3857')
    country2 = country2.to_crs('EPSG:3857')

    # Calculate the centroids of the countries
    country1_centroid = country1['geometry'].centroid
    country2_centroid = country2['geometry'].centroid

    # Calculate the differences in x and y coordinates
    diff_x = country2_centroid.x.squeeze() - country1_centroid.x.squeeze()
    diff_y = country2_centroid.y.squeeze() - country1_centroid.y.squeeze()

    # Determine the dominant orientation based on the differences
    if abs(diff_y) > abs(diff_x):
        if diff_y > 0:
            orientation = "north"
        else:
            orientation = "south"
    else:
        if diff_x > 0:
            orientation = "east"
        else:
            orientation = "west"

    return orientation



        
def display_errors():
    for elem in st.session_state.choice_list[1:len(st.session_state.choice_list)]:
        if elem != '':
            present_country_geom_data = get_geom_data_from_name(st.session_state.present_country_name)
            country_input = get_geom_data_from_name(elem)
            dist = get_distance(country_input, present_country_geom_data)
            orient = get_orientation(country_input, present_country_geom_data)
            if orient == "north":
                st.write(f"{elem} distance: {dist}km :arrow_up:")
            elif orient == "south":
                st.write(f"{elem} distance: {dist}km :arrow_down:")
            elif orient == "west":
                st.write(f"{elem} distance: {dist}km :arrow_left:")
            else:
                st.write(f"{elem} distance: {dist}km :arrow_right:")

            

def display_game():
    col1, col2, col3 = st.columns(3)
    with col2:

        with st.form("my_form"):
            st.markdown("<h1 style='text-align: center; color: green;'>Oh le zin c koi ce pays la ?</h1>", unsafe_allow_html=True)
            
            # At the init or when a game is won, we go through this to select a new country to display
            if st.session_state.pick_new_country:
                thisCountryName = get_random_country(df)
                st.session_state.pick_new_country = False
                # st.session_state['present_country'] = thisCountryName
                st.session_state['present_country_name'] = thisCountryName

            display_country(st.session_state['present_country_name'])

            ################ DISPLAY FORM FROM HERE ################
            col11, col12, col13 = st.columns([1,10,1])
            with col12:
                country_list = [''] + get_country_list(df)
                choice = st.selectbox(label = "Country:", options = country_list, key='countrySelected')
                st.session_state.choice_list.append(choice)


                ################ SUBMIT FUNCTION HERE ################
                submitted = st.form_submit_button("Submit")
                if submitted:
                    print(type(st.session_state.choice_list[-1]))
                    print(type(st.session_state.present_country_name))
                    if st.session_state.present_country_name == st.session_state.choice_list[-1]:
                        st.markdown("<h1 style='text-align: center; color: green;'>BIEN VU BGGGGG</h1>", unsafe_allow_html=True)
                        st.session_state.reset_game = True
                    else:
                        display_errors()

# Check the nan value errors
# TODO: reset choice when submitting

display_game()

if st.session_state.reset_game:
    col1, col2, col3 = st.columns([3,2,3])
    with col2:
        st.button("Ca repart pour ou tour ouuuuuu ?", key=None, help=None, on_click=reset_game(),  use_container_width=False)
