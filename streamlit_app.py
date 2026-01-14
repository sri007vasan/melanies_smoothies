# Import python packages
import streamlit as st
import requests
from snowflake.snowpark.functions import col

# Page title
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

# Name input
name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your Smoothie will be:", name_on_order)

# Get Snowflake session
cnx = st.connection("snowflake")
session = cnx.session()

# Load fruit table
my_dataframe = session.table("smoothies.public.fruit_options")

# Convert fruit names to Python list
fruit_list = my_dataframe.select(col("FRUIT_NAME")).to_pandas()["FRUIT_NAME"].tolist()

# Multiselect
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_list,
    max_selections=5
)

# Only run if user selected something
if ingredients_list:

    ingredients_string = ""
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + " "

    # Try API (Snowflake blocks external calls, so fail safely)
    try:
        smoothieroot_response = requests.get("https://my.smoothieroot.com/api/fruit/watermelon", timeout=5)
        st.dataframe(smoothieroot_response.json(), use_container_width=True)
    except:
        st.warning("External API not reachable (Snowflake blocks public internet).")

    # Submit button
    time_to_insert = st.button("Submit Order")

    if time_to_insert:
        session.sql(
            "INSERT INTO smoothies.public.orders (ingredients, name_on_order) VALUES (?, ?)",
            params=[ingredients_string, name_on_order]
        ).collect()

        st.success("Your Smoothie is ordered!", icon="✅")
