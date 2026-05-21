# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests  



# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("""
Choose the fruits you want in your custom Smoothie!
""")



name_on_order = st.text_input("Name on Smoothie: ")
st.write("The name on your Smoothie will be: ", name_on_order)

cnx = st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))
# st.dataframe(data=my_dataframe, use_container_width=True)


#----------------------------------------------------------------------------------------------------------------
# Step 1: Add column
session.sql("""
ALTER TABLE FRUIT_OPTIONS
ADD COLUMN SEARCH_ON STRING
""").collect()

# Step 2: Custom values
session.sql("""
UPDATE FRUIT_OPTIONS
SET SEARCH_ON = 'apple fruit'
WHERE FRUIT_NAME = 'Apple'
""").collect()

# Step 3: Default remaining rows
session.sql("""
UPDATE FRUIT_OPTIONS
SET SEARCH_ON = FRUIT_NAME
WHERE SEARCH_ON IS NULL
""").collect()
#-----------------------------------------------------------------------------------------------------------------


ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:'
    , my_dataframe
    , max_selections=5
)

if ingredients_list:
    ingredients_string = ''

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '
        st.subheader(fruit_chosen + ' Nutrition Information')
        smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/" + fruit_chosen)  
        sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)

    # st.write(ingredients_string)


    my_insert_stmt = """ insert into smoothies.public.orders(ingredients, name_on_order)
                    values ('""" + ingredients_string + """','"""+name_on_order+"""')"""

    st.write(my_insert_stmt)
    
    
    time_to_insert = st.button('Submit Order')
    
    # st.write(my_insert_stmt)
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success(f'Your Smoothie is ordered, {name_on_order}!', icon="✅")
    st.stop()



