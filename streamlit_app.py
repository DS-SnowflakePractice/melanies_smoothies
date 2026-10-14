# Import python packages
import streamlit as st
import requests

from snowflake.snowpark.functions import col

# Create Snowflake Session
cnx = st.connection("snowflake")
session = cnx.session()

# Page Title
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")

st.write(
    "Choose the fruits you want in your custom Smoothie!"
)

# Customer Name
name_on_order = st.text_input("Name on Smoothie:")

st.write("The name on your Smoothie will be:", name_on_order)

# Fruit Options from Snowflake
fruit_df = (
    session.table("SMOOTHIES.PUBLIC.FRUIT_OPTIONS")
    .select(
        col("FRUIT_NAME"),
        col("SEARCH_ON")
    )
)

fruit_rows = fruit_df.collect()

fruit_list = [row["FRUIT_NAME"] for row in fruit_rows]

# Ingredient Selector
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_list,
    max_selections=5
)

if ingredients_list:

    ingredients_string = ""

    for fruit_chosen in ingredients_list:

        ingredients_string += fruit_chosen + " "

        # Get SEARCH_ON value for selected fruit
        search_on = next(
            row["SEARCH_ON"]
            for row in fruit_rows
            if row["FRUIT_NAME"] == fruit_chosen
        )

        st.subheader(
            fruit_chosen + " Nutrition Information"
        )

        smoothiefroot_response = requests.get(
            f"https://my.smoothiefroot.com/api/fruit/{search_on}"
        )

        st.dataframe(
            data=smoothiefroot_response.json(),
            use_container_width=True
        )

    my_insert_stmt = f"""
    INSERT INTO SMOOTHIES.PUBLIC.ORDERS
    (INGREDIENTS, NAME_ON_ORDER)
    VALUES
    ('{ingredients_string}', '{name_on_order}')
    """

    time_to_insert = st.button("Submit Order")

    if time_to_insert:

        session.sql(my_insert_stmt).collect()

        st.success(
            "Your Smoothie is ordered!",
            icon="✅"
        )
