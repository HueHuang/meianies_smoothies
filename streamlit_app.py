# Import python packages
import streamlit as st
import pandas  as pd
from snowflake.snowpark.functions import col
import requests


# Write directly to the app
st.title(":cup_with_straw: Customize your smoothie :cup_with_straw: ")
st.write(
    """Choose the fruits you want in your custom smoothie
    """)
name_on_order = st.text_input("Name of smoothie:", "Life of Brian")
st.write("The name on your smoothie would be:", name_on_order)

cnx = st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))
st.dataframe(data=my_dataframe, use_container_width=True)

pd_df = my_dataframe.to_pandas()

ingredients_list = st.multiselect(
    "CHOOSE UP TO 5 INGREDIENTS",
    my_dataframe
)

if ingredients_list and name_on_order:

    ingredients_string = ''
    name = name_on_order

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '
        
        search_on=pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        # st.write('The search value for ', fruit_chosen,' is ', search_on, '.')
        
        st.subheader(fruit_chosen + 'Nutrition Information')
        smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/" + search_on)
        sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
                

    # st.write(ingredients_string)

    my_insert_stmt = """ insert into smoothies.public.orders(ingredients, name_on_order)
            values ('""" + ingredients_string + """','""" + name + """')"""

    # st.write(my_insert_stmt)
    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success(f'Your Smoothie is ordered, {name}!', icon="✅")
