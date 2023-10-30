import streamlit as st
from datetime import datetime, timedelta
from functions.query import query_results

def date_filter(dest, db, sc, md='bs', k=1):
    
    data = query_results(destination=dest, database=db, schema=sc, model=md)

    # Create a mapping from 'account_period_name' to 'account_period_ending'
    date_name_mapping = {row['accounting_period_ending']: row['accounting_period_name'] for _, row in data.iterrows()}

    distinct_dates = list(set(data.copy()['accounting_period_ending']))
    sorted_month_end_dates = sorted(distinct_dates, reverse=True)

    # Get the corresponding 'account_period_name' for display
    sorted_period_names = [date_name_mapping[date] for date in sorted_month_end_dates]

    # Set default dates if not in session state
    if 'start_month' not in st.session_state or 'end_month' not in st.session_state:
        most_recent_date = sorted_month_end_dates[0]
        st.session_state.start_month = date_name_mapping[most_recent_date]
        st.session_state.end_month = date_name_mapping[most_recent_date]

    selected_start_month_name = st.selectbox("Select start month", sorted_period_names, index=sorted_period_names.index(st.session_state.start_month), key=str(k)+"_start")
    selected_end_month_name = st.selectbox("Select end month", sorted_period_names, index=sorted_period_names.index(st.session_state.end_month), key=str(k)+"_end")

    # Get the corresponding 'account_period_ending' value for return
    selected_start_month = [date for date, name in date_name_mapping.items() if name == selected_start_month_name][0]
    selected_end_month = [date for date, name in date_name_mapping.items() if name == selected_end_month_name][0]

    st.write(f"Selected date range: month ending {selected_start_month} to month ending {selected_end_month}")

    # Update the session state values based on the user's selections.
    st.session_state.start_month = selected_start_month_name
    st.session_state.end_month = selected_end_month_name

    return data, [selected_start_month, selected_end_month]

def filter_data(start, end, data_ref, model='bs'):
    if model == "bs" or model == 'is':
        data_date_filtered = data_ref.query("`accounting_period_ending` >= @start and `accounting_period_ending` <= @end")

    return data_date_filtered

def extract_second_item(s):
    parts = [part.strip() for part in s.split(":")]
    return parts[1] if len(parts) > 1 else None