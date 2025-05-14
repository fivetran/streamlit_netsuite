import streamlit as st
import plost
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime
from functions.filters import date_filter, filter_data
from functions.variables import database_schema_variables, destination_selection
from functions.query import query_results

## Apply standard page settings.
st.set_page_config(
    layout="wide",
    initial_sidebar_state="expanded",
)

st.sidebar.header('Data Connection Variables')
destination = destination_selection()
database, schema = database_schema_variables()

st.title('Profit and Loss Dashboard')

if destination in ("BigQuery","Snowflake") and (database in ("Database", "None") or schema in ("Schema", "None")):
    st.warning('To leverage your own internal data, you will need to fork this repo and deploy as your own Streamlit app. Please see the README for additional details.')
else:
    # data_all = query_results(destination=destination, database=database, schema=schema, model='is')
    data, d = date_filter(dest=destination, db=database, sc=schema, md='is')

    ## Only generate the tiles if date range is populated
    if d is not None and len(d) == 2:
        start_date, end_date = d
        if start_date is not None and start_date <= end_date:
            ## Filter data based on filters applied
            data_date_filtered = filter_data(start=start_date, end=end_date, data_ref=data, model='is')

            ## Period specific information
            if start_date == end_date:
                st.title(f'{start_date.strftime("%b %Y")} period profit and loss report')
            else:
                st.title(f'{start_date.strftime("%b %Y")} to {end_date.strftime("%b %Y")} period profit and loss report')

            st.markdown('---')
            ## Create the primary income statement view
            # st.subheader("Profit and Loss Statement")
            df = data_date_filtered.copy()
            
            df['formatted_balance'] = df['balance'].apply(lambda x: "${:,.2f}".format(x))
            for category in df['account_category'].unique():
                # st.subheader(category)
                
                category_data = df[df['account_category'] == category]
                st.subheader(f"**{category}**")
                # Expansion for different account types under the category
                for account_type in category_data['account_type_name'].unique():
                    account_type_data = category_data[category_data['account_type_name'] == account_type]
                    
                    # Calculate the subtotal for the account type
                    subtotal_account_type = "${:,.2f}".format(account_type_data['balance'].sum())

                    # Custom title that includes account type name and its total sum
                    expander_title = f"**{account_type}**: {subtotal_account_type}"
                    
                    with st.expander(expander_title):  # User can collapse/expand data for each account type
                        st.table(account_type_data[['account_name', 'formatted_balance']])
                        
                        # Display the subtotal for the account type inside the expander as well (optional)
                        st.write(f"**Total {account_type}:** {subtotal_account_type}")

                # Display the subtotal for the category
                subtotal = "${:,.2f}".format(category_data['balance'].sum())
                st.write(f"**Total {category}:** {subtotal}")
            
            revenue = df[df['account_category'] == 'Income']['balance'].sum()
            exp = df[df['account_category'] == 'Expense']['balance'].sum()

            # Calculate Gross Margin
            gross_margin = revenue - exp * - 1

            # Display Gross Margin
            st.subheader("Net Profit")
            st.write("${:,.2f}".format(gross_margin))
        else:
            st.warning("Please ensure your starting period is before your ending period.")
