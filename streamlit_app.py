# Import python packages
import streamlit as st
import requests

from snowflake.snowpark.functions import col

cnx = st.connection("snowflake")
session = cnx.session()

st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")

st.write(
    """Choose the fruits you want in your custom Smoothie!"""
)

name_on_order = st.text_input("Name on Smoothie:")

st.write("The name on your Smoothie will be:", name_on_order)

fruit_df = session.table(
    "SMOOTHIES.PUBLIC.FRUIT_OPTIONS"
).select(col("FRUIT_NAME"))

fruit_list = [row["FRUIT_NAME"] for row in fruit_df.collect()]

ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_list,
    max_selections=5
)

if ingredients_list:

    ingredients_string = ''

    for fruit_chosen in ingredients_list:

        ingredients_string += fruit_chosen + ' '

        # Lesson 11 code goes INSIDE the loop
        smoothiefroot_response = requests.get(
            "https://my.smoothiefroot.com/api/fruit/watermelon"
        )

        sf_df = st.dataframe(
            data=smoothiefroot_response.json(),
            use_container_width=True
        )

    my_insert_stmt = f"""
    INSERT INTO SMOOTHIES.PUBLIC.ORDERS
    (INGREDIENTS, NAME_ON_ORDER)
    VALUES
    ('{ingredients_string}', '{name_on_order}')
    """

    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered!', icon="✅")
`
