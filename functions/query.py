import streamlit as st
import pandas as pd
from google.oauth2 import service_account
from google.cloud import bigquery

# Grab global variables
destination = st.session_state.destination
database = st.session_state.database 
schema = st.session_state.schema

# Perform query.
# Uses st.cache_data to only rerun when the query changes or after 10 min.
@st.cache_data(ttl=600)
def run_query(query):
    # Create API client.
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"]
    )
    client = bigquery.Client(credentials=credentials)
    query_job = client.query(query)
    rows_raw = query_job.result()
    # Convert to list of dicts. Required for st.cache_data to hash the return value.
    rows = [dict(row) for row in rows_raw]
    return rows

def query_results(destination, database, schema, model='bs'):
    if destination == "BigQuery" and model == "bs":
        if database is None or schema is None:
            st.warning("Results will be displayed once your database and schema are provided.")
        else:
            query = run_query(
                "select "\
                    "balance_sheet_sort_helper, "\
                    "accounting_period_name, "\
                    "accounting_period_ending, "\
                    "account_category, "\
                    "account_name, "\
                    "account_type_name, "\
                    "round(sum(converted_amount),2) as balance "\
                "from `" + database + "." + schema + ".netsuite2__balance_sheet` "\
                "group by 1,2,3,4,5,6 order by balance_sheet_sort_helper"
            )

    if destination == "BigQuery" and model == "is":
        if database is None or schema is None:
            st.error("Results will be displayed once your database and schema are provided.")
        else:
            query = run_query(
                "select "\
                    "income_statement_sort_helper, "\
                    "accounting_period_name, "\
                    "accounting_period_ending, "\
                    "account_category, "\
                    "account_name, "\
                    "account_type_name, "\
                    "round(sum(converted_amount),2) as balance "\
                "from `" + database + "." + schema + ".netsuite2__income_statement` "\
                "group by 1,2,3,4,5,6 order by income_statement_sort_helper"
            )

    if destination == "Snowflake" and model == "bs":
        if database is None or schema is None:
            st.warning("Results will be displayed once your database and schema are provided.")
        else:
            conn = st.experimental_connection('snowpark')
            query_job = conn.query(
                "select "\
                    "balance_sheet_sort_helper, "\
                    "accounting_period_name, "\
                    "accounting_period_ending, "\
                    "account_category, "\
                    "account_name, "\
                    "account_type_name, "\
                    "round(sum(converted_amount),2) as balance "\
                "from `" + database + "." + schema + ".netsuite2__balance_sheet` "\
                "group by 1,2,3,4,5,6 order by balance_sheet_sort_helper"
            )
            raw_results = query_job.result()
            # Convert to list of dicts. Required for st.cache_data to hash the return value.
            query = [dict(row) for row in raw_results]

    if destination == "Snowflake" and model == "is":
        if database is None or schema is None:
            st.warning("Results will be displayed once your database and schema are provided.")
        else:
            conn = st.experimental_connection('snowpark')
            query_job = conn.query(
                "select "\
                    "income_statement_sort_helper, "\
                    "accounting_period_name, "\
                    "accounting_period_ending, "\
                    "account_category, "\
                    "account_name, "\
                    "account_type_name, "\
                    "round(sum(converted_amount),2) as balance "\
                "from `" + database + "." + schema + ".netsuite2__income_statement` "\
                "group by 1,2,3,4,5,6 order by income_statement_sort_helper"
            )
            raw_results = query_job.result()
            # Convert to list of dicts. Required for st.cache_data to hash the return value.
            query = [dict(row) for row in raw_results]

    if destination == "Dunder Mifflin Sample Data" and model == "is":
        query = pd.read_csv('data/dunder_mifflin_income_statement.csv')

        ## Convert csv fields for time conversions later on
        query['accounting_period_ending'] = pd.to_datetime(query['accounting_period_ending'])

    if destination == "Dunder Mifflin Sample Data" and model == "bs":
        query = pd.read_csv('data/dunder_mifflin_balance_sheet.csv')

        ## Convert csv fields for time conversions later on
        query['accounting_period_ending'] = pd.to_datetime(query['accounting_period_ending'])

    if model == 'bs':
        data = pd.DataFrame(query, columns=['balance_sheet_sort_helper','accounting_period_name','accounting_period_ending','account_category','account_name','account_type_name','balance'])

        # Get the data into the app and specify any datatypes if needed.
        data_load_state = st.text('Loading data...')
        data['accounting_period_ending'] = data['accounting_period_ending'].dt.date
        data_load_state.text("Done! (using st.cache_data)")
    if model == 'is':
        data = pd.DataFrame(query, columns=['income_statement_sort_helper','accounting_period_name','accounting_period_ending','account_category','account_name','account_type_name','balance'])
        # Get the data into the app and specify any datatypes if needed.
        data_load_state = st.text('Loading data...')
        data['accounting_period_ending'] = data['accounting_period_ending'].dt.date
        data_load_state.text("Done! (using st.cache_data)")
        
    return data