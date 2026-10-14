# Import python packages
import streamlit as st
import requests

from snowflake.snowpark.functions import col

# Create Snowflake session
cnx = st.connection("snowflake")
session = cnx.session()

# Page title
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")

st.write(
    """Choose the fruits you want in your custom Smoothie!"""
)

# Name field
name_on_order = st.text_input("Name on Smoothie:")

st.write("The name on your Smoothie will be:", name_on_order)

# Fruit list from Snowflake
fruit_df = session.table(
    "SMOOTHIES.PUBLIC.FRUIT_OPTIONS"
).select(col("FRUIT_NAME"))

fruit_list = [row["FRUIT_NAME"] for row in fruit_df.collect()]

# Ingredient selector
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_list,
    max_selections=5
)

# Submit order
if ingredients_list:

    ingredients_string = ", ".join(ingredients_list)

    my_insert_stmt = f"""
    INSERT INTO SMOOTHIES.PUBLIC.ORDERS
    (INGREDIENTS, NAME_ON_ORDER)
    VALUES
    ('{ingredients_string}', '{name_on_order}')
    """

    if st.button("Submit Order"):
        session.sql(my_insert_stmt).collect()
        st.success("Your Smoothie is ordered!", icon="✅")

# New section to display SmoothieFroot nutrition information
smoothiefroot_response = requests.get(
    "https://my.smoothiefroot.com/api/fruit/watermelon"
)

# st.text(smoothiefroot_response.json())

sf_df = st.dataframe(
    data=smoothiefroot_response.json(),
    use_container_width=True
)
