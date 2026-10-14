# Import python packages
import streamlit as st
import requests
import pandas as pd

from snowflake.snowpark.functions import col

# Create Snowflake Session
cnx = st.connection("snowflake")
session = cnx.session()

# Page Title
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")

st.write(
    """Choose the fruits you want in your custom Smoothie!"""
)

# Customer Name
name_on_order = st.text_input("Name on Smoothie:")

st.write("The name on your Smoothie will be:", name_on_order)

# Get Fruit List from Snowflake
fruit_df = (
    session.table("SMOOTHIES.PUBLIC.FRUIT_OPTIONS")
    .select(col("FRUIT_NAME"))
)

fruit_list = [row["FRUIT_NAME"] for row in fruit_df.collect()]

# Ingredient Selection
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_list,
    max_selections=5
)

# SmoothieFroot Nutrition Information
if ingredients_list:

    fruit_choice = ingredients_list[0]

    st.subheader("Nutrition Information")

    try:
        smoothiefroot_response = requests.get(
            f"https://my.smoothiefroot.com/api/fruit/{fruit_choice.lower()}"
        )

        if smoothiefroot_response.status_code == 200:

            try:
                fruit_data = pd.json_normalize(
                    smoothiefroot_response.json()
                )

                st.dataframe(
                    fruit_data,
                    use_container_width=True
                )

            except Exception:
                st.error("The API returned data that is not valid JSON.")

        else:
            st.error(
                f"API request failed with status code "
                f"{smoothiefroot_response.status_code}"
            )

    except Exception as e:
        st.error(f"Unable to retrieve fruit data: {e}")

# Submit Order
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
