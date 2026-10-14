import requests 
import streamlit as st
from snowflake.snowpark.functions import col

cnx = st.connection("snowflake")
session = cnx.session()

st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")

name_on_order = st.text_input("Name on Smoothie:")

fruit_df = session.table(
    "smoothies.public.fruit_options"
).select(col("FRUIT_NAME"))

fruit_list = [row["FRUIT_NAME"] for row in fruit_df.collect()]

ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_list,
    max_selections=5
)

if ingredients_list:

    ingredients_string = " ".join(ingredients_list)

    my_insert_stmt = f"""
    INSERT INTO smoothies.public.orders
    (ingredients, name_on_order)
    VALUES
    ('{ingredients_string}', '{name_on_order}')
    """

    st.write(my_insert_stmt)

    if st.button("Submit Order"):
        session.sql(my_insert_stmt).collect()
        st.success("Your Smoothie is ordered!", icon="✅")




smoothiefroot_response = requests.get(
    "https://my.smoothiefroot.com/api/fruit/watermelon"
)  
# st.text(smoothiefroot_response.json)
sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
