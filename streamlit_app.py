# Import python packages
import streamlit as st
import requests
import pandas as pd

from snowflake.snowpark.functions import col

# Create Snowflake Session
cnx = st.connection("snowflake")
session = cnx.session()

# Page title
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")

st.write(
    """Choose the fruits you want in your custom Smoothie!"""
)

# Customer name
name_on_order = st.text_input("Name on Smoothie:")

st.write("The name on your Smoothie will be:", name_on_order)

# Fruit list from Snowflake
fruit_df = (
    session.table("SMOOTHIES.PUBLIC.FRUIT_OPTIONS")
    .select(col("FRUIT_NAME"))
)

fruit_list = [row["FRUIT_NAME"] for row in fruit_df.collect()]

# Fruit selector
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_list,
    max_selections=5
)

# Display API data
if ingredients_list:

    fruit_choice = ingredients_list[0]

    smoothiefroot_response = requests.get(
        f"https://my.smoothiefroot.com/api/fruit/{fruit_choice.lower()}"
    )

    if smoothiefroot_response.status_code == 200:

        sf_df = pd.json_normalize(
            smoothiefroot_response.json()
        )

        st.dataframe(
            sf_df,
            use_container_width=True
        )

# Submit order
if ingredients_list and st.button("Submit Order"):

    ingredients_string = ", ".join(ingredients_list)

    my_insert_stmt = f"""
    INSERT INTO SMOOTHIES.PUBLIC.ORDERS
    (INGREDIENTS, NAME_ON_ORDER)
    VALUES
    ('{ingredients_string}', '{name_on_order}')
    """

    session.sql(my_insert_stmt).collect()

    st.success("Your Smoothie is ordered!", icon="✅")
