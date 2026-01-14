# Import python packages
import streamlit as st
import pandas as pd
import requests
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col

# App title
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

# Name input
name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your Smoothie will be:", name_on_order)

# Create Snowflake session
session = get_active_session()

# Pull FRUIT_NAME and SEARCH_ON from Snowflake
my_dataframe = (
    session.table("smoothies.public.fruit_options")
           .select(col("FRUIT_NAME"), col("SEARCH_ON"))
)

# Convert Snowpark → Pandas so we can use LOC
pd_df = my_dataframe.to_pandas()

# Show table so we can confirm SEARCH_ON is correct
st.dataframe(pd_df, use_container_width=True)

# Multiselect uses only FRUIT_NAME column
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    pd_df["FRUIT_NAME"].tolist(),
    max_selections=5
)

# Only run when fruits selected
if ingredients_list:

    ingredients_string = ""

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + " "

        # 🥋 LOOKUP SEARCH_ON VALUE
        search_on = pd_df.loc[
            pd_df["FRUIT_NAME"] == fruit_chosen,
            "SEARCH_ON"
        ].iloc[0]

        st.write("The search value for", fruit_chosen, "is", search_on, ".")

        # Call the API using SEARCH_ON (Snowflake training pattern)
        try:
            fruityvice_response = requests.get(
                "https://fruityvice.com/api/fruit/" + search_on
            )
            st.subheader(fruit_chosen + " Nutrition Information")
            st.dataframe(fruityvice_response.json(), use_container_width=True)

        except:
            st.warning("External API not reachable in Snowflake environment.")

    # Submit order button
    time_to_insert = st.button("Submit Order")

    if time_to_insert:
        session.sql(
            "INSERT INTO smoothies.public.orders (ingredients, name_on_order) VALUES (?, ?)",
            params=[ingredients_string, name_on_order]
        ).collect()

        st.success("Your Smoothie is ordered!", icon="✅")
