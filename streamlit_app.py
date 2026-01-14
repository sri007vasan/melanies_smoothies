from snowflake.snowpark.functions import col, when_matched
import streamlit as st

# Write directly to the app
st.title(":cup_with_straw: Pending Smoothie Orders :cup_with_straw:")
st.write("Orders that need to be filled.")

# Create Snowflake session
cnx=st.connection("snowflake")
session = cnx.session()

# Get only unfilled orders
my_dataframe = (
    session.table("smoothies.public.orders")
           .filter(col("ORDER_FILLED") == False)
)

# If there are pending orders
if my_dataframe.count() > 0:

    # Show editable table
    editable_df = st.data_editor(my_dataframe, use_container_width=True)

    submitted = st.button("Submit")

    if submitted:
        try:
            # Convert edited data back to Snowpark DataFrame
            edited_dataset = session.create_dataframe(editable_df)

            # Original Snowflake table
            og_dataset = session.table("smoothies.public.orders")

            # Merge updates
            og_dataset.merge(
                edited_dataset,
                og_dataset["ORDER_UID"] == edited_dataset["ORDER_UID"],
                [when_matched().update({"ORDER_FILLED": edited_dataset["ORDER_FILLED"]})]
            )

            st.success("Order(s) Updated!", icon="🍓")

        except:
            st.write("Something went wrong.")

else:
    st.success("There are no pending orders right now.", icon="👍")
