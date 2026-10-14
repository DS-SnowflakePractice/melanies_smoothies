# Import python packages
import streamlit as st
import requests
import pandas as pd

from snowflake.snowpark.functions import col

# Create Snowflake session
cnx = st.connection("snowflake")
session = cnx.session()

# Page Title
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")

# Customer Name
name_on_order = st.text_input("Name on Smoothie:")

# Get fruit options from Snowflake
fruit_df = (
    session.table("SMOOTHIES.PUBLIC.FRUIT_OPTIONS")
    .select(col("FRUIT_NAME"))
)

fruit_list = [row["FRUIT_NAME"] for row in fruit_df.collect()]

# Fruit Selection
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_list,
    max_selections=5
)

# Show nutritional information
if ingredients_list:

    st.subheader("Fruit Nutrition Information")

    for fruit_chosen in ingredients_list:

        smoothiefroot_response = requests.get(
            f"https://my.smoothiefroot.com/api/fruit/{fruit_chosen}"
        )

        if smoothiefroot_response.status_code == 200:

            fruit_data = pd.json_normalize(
                smoothiefroot_response.json()
            )

            st.dataframe(
                fruit_data,
                use_container_width=True
            )

# Order Submission
if ingredients_list and name_on_order:

    ingredients_string = ", ".join(ingredients_list)

    my_insert_stmt = f"""
    INSERT INTO SMOOTHIES.PUBLIC.ORDERS
    (INGREDIENTS, NAME_ON_ORDER)
    VALUES
    ('{ingredients_string}', '{name_on_order}')
    """

    if st.button("Submit Order"):

        session.sql(my_insert_stmt).collect()

        st.success(
            f"Your smoothie for {name_on_order} has been ordered!",
            icon="✅"
        )
