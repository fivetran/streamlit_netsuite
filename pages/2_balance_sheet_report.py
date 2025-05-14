import streamlit as st
import plost
import pandas as pd
import numpy as np
from datetime import datetime
from functions.filters import date_filter, filter_data
from functions.variables import database_schema_variables, destination_selection

## Apply standard page settings.
st.set_page_config(
    layout="wide",
    initial_sidebar_state="expanded",
)

st.sidebar.header('Data Connection Variables')
destination = destination_selection()
database, schema = database_schema_variables()

st.title('Balance Sheet Dashboard')

if destination in ("BigQuery","Snowflake") and (database in ("Database", "None") or schema in ("Schema", "None")):
    st.warning('To leverage your own internal data, you will need to fork this repo and deploy as your own Streamlit app. Please see the README for additional details.')
else:

    ## Define the top level date filter
    st.header("Balance Sheet Details by Period")
    data, d = date_filter(dest=destination, db=database, sc=schema)

    ## Only generate the tiles if date range is populated
    if d is not None and len(d) == 2:
        start_date, end_date = d
        if start_date is not None and start_date <= end_date:
            ## Filter data based on filters applied
            data_date_filtered = filter_data(start=start_date, end=end_date, data_ref=data)

            ## Period specific information
            if start_date == end_date:
                st.title(f'{start_date.strftime("%b %Y")} period balance sheet')
            else:
                st.title(f'{start_date.strftime("%b %Y")} to {end_date.strftime("%b %Y")} period balance sheets')
            st.markdown('<hr style="height:2px;border:none;color:#333;background-color:#333;" />', unsafe_allow_html=True)

            ## Create the primary balance sheet view
            df = data_date_filtered.copy()
            df = df[~df['account_category'].isin(['Income', 'Expense'])]

            df['formatted_balance'] = df['balance'].apply(lambda x: "${:,.2f}".format(float(x)))

            # Sort unique periods by accounting_period_ending in descending order
            sorted_periods = sorted(df['accounting_period_ending'].unique(), reverse=True)

            first_run = True
            for accounting_period in sorted_periods:
                period_name = df[df['accounting_period_ending'] == accounting_period]['accounting_period_name'].iloc[0]
                if not first_run:
                    st.markdown('---')
                st.title(period_name)  # Use a title to clearly separate each accounting period

                period_data = df[df['accounting_period_ending'] == accounting_period]

                for category in period_data['account_category'].unique():
                    st.header(category)  # Display the account_category as a header

                    category_data = period_data[period_data['account_category'] == category]

                    for account_type in category_data['account_type_name'].unique():
                        account_type_data = category_data[category_data['account_type_name'] == account_type]

                        # Calculate the subtotal for the account type
                        subtotal_account_type = "${:,.2f}".format(account_type_data['balance'].astype(float).sum())

                        # Custom title that includes account type name and its total sum
                        expander_title = f"{account_type}: {subtotal_account_type}"
                        
                        # Create an expander for each account_type_name within the account_category
                        with st.expander(expander_title):
                            st.table(account_type_data[['account_name', 'formatted_balance']])

                        # Display the subtotal for the category
                        subtotal = "${:,.2f}".format(category_data['balance'].astype(float).sum())
                    st.write(f"**Total {category}:** {subtotal}")
                first_run = False
        else:
            st.warning("Please ensure your starting period is before your ending period.")
