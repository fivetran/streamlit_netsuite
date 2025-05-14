import streamlit as st
import plost
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from functions.filters import date_filter, filter_data, extract_second_item
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

st.title('Financial Executive Dashboard')

if destination in ("BigQuery","Snowflake") and (database in ("Database", "None") or schema in ("Schema", "None")):
    st.warning('To leverage your own internal data, you will need to fork this repo and deploy as your own Streamlit app. Please see the README for additional details.')
else:

    ## Define the top level date filter
    st.subheader("Period(s) in review")
    data, d = date_filter(dest=destination, db=database, sc=schema, md='bs')
    bs_data = data
    is_data = query_results(destination=destination, database=database, schema=schema, model='is')

    ## Only generate the tiles if date range is populated
    if d is not None and len(d) == 2:
        start_date, end_date = d
        if start_date is not None and start_date <= end_date:
            ## Filter data based on filters applied
            is_data_date_filtered = filter_data(start=start_date, end=end_date, data_ref=is_data, model='is')
            bs_data_date_filtered = filter_data(start=start_date, end=end_date, data_ref=bs_data, model='bs')

            ## KPI Metrics
            st.markdown('<hr style="height:2px;border:none;color:#333;background-color:#333;" />', unsafe_allow_html=True)
            st.subheader('High Level Balance and Totals')

            metrics_data = bs_data_date_filtered.copy()
            col1, col2 = st.columns(2)

            metrics_data['accounting_period_ending'] = pd.to_datetime(metrics_data['accounting_period_ending'])
            latest_date = metrics_data['accounting_period_ending'].max()

            latest_current_assets = metrics_data[
                (metrics_data['accounting_period_ending'] == latest_date) &
                (metrics_data['account_category'].str.lower() == 'asset')
            ]

            latest_current_liabilities = metrics_data[
                (metrics_data['accounting_period_ending'] == latest_date) &
                (metrics_data['account_category'].str.lower() == 'liability')
            ]

            latest_cash_data = metrics_data[
                (metrics_data['accounting_period_ending'] == latest_date) &
                metrics_data['account_name'].str.lower().str.contains('cash and cash equivalents', case=False, na=False)
            ]

            latest_inventory_data = metrics_data[
                (metrics_data['accounting_period_ending'] == latest_date) &
                metrics_data['account_name'].str.lower().str.contains('inventory', case=False, na=False)
            ]
            current_assets = latest_current_assets['balance'].astype(float).sum()
            current_liabilities = latest_current_liabilities['balance'].astype(float).sum()
            inventory = latest_inventory_data['balance'].astype(float).sum()

            metrics_data['accounting_period_ending'] = pd.to_datetime(metrics_data['accounting_period_ending'])
            latest_date = metrics_data.copy()['accounting_period_ending'].max()
            
            ## Cash balance and working capital
            with col1:
                working_capital = current_assets - current_liabilities
                formatted_working_capital = "${:,.2f}".format(working_capital)
                st.metric("Working Capital", formatted_working_capital, delta=None, delta_color="normal", help=None, label_visibility="visible")

            with col2:
                cash_balance = latest_cash_data['balance'].astype(float).sum()
                formatted_cash_balance = "${:,.2f}".format(cash_balance)
                st.metric("Cash Balance", formatted_cash_balance, delta=None, delta_color="normal", help=None, label_visibility="visible")

            metric_df = is_data_date_filtered.copy()
            # Convert balance to float for calculations
            metric_df['balance'] = metric_df['balance'].astype(float)

            # Calculate revenue and COGS
            revenue = metric_df[metric_df['account_category'] == 'Income']['balance'].sum()
            cogs = metric_df[metric_df['account_type_name'] == 'Cost of Goods Sold']['balance'].sum()
            opp_expense = metric_df[metric_df['account_type_name'] == 'Expense']['balance'].sum()
            all_expense = metric_df[metric_df['account_category'] == 'Expense']['balance'].sum()

            # Calculate Gross Profit and Gross Profit Margin
            gross_profit_cogs = revenue - (cogs * -1)
            gross_profit_exp = revenue - (opp_expense * -1)
            net_profit = revenue - (all_expense * -1)

            # Calculate Ratios
            opex_ratio = opp_expense / revenue
            gross_profit_margin = (gross_profit_cogs / revenue) * 100
            operating_profit_margin = (gross_profit_exp / revenue) * 100
            net_profit_margin = (net_profit / revenue) * 100

            col1, col2 = st.columns(2)
            with col1:
                formatted_revenue = "${:,.2f}".format(revenue)
                st.metric("Revenue", formatted_revenue, delta=None, delta_color="normal", help=None, label_visibility="visible")
            with col2:
                adj_opp_expense = opp_expense * -1
                formatted_opp_expense = "${:,.2f}".format(adj_opp_expense)
                st.metric("Operating Expenses", formatted_opp_expense, delta=None, delta_color="normal", help=None, label_visibility="visible")
            
            st.markdown("---")

            col1, col2 = st.columns(2)
            with col1:
                # formatted_gross_profit_cogs = "${:,.2f}".format(gross_profit_cogs)
                gross_profit_color = "green" if gross_profit_cogs >= 0 else "red"
                formatted_gross_profit_cogs = "${:,.2f}".format(gross_profit_cogs)
                gross_profit_display = f'<div style="font-size:35px; font-weight:bold; color: {gross_profit_color}">{formatted_gross_profit_cogs}</div>'

                st.markdown("Gross Profit", unsafe_allow_html=True)
                st.markdown(gross_profit_display, unsafe_allow_html=True)

            with col2:
                net_profit_color = "green" if net_profit >= 0 else "red"
                formatted_net_profit = "${:,.2f}".format(net_profit)
                net_profit_display = f'<div style="font-size:35px; font-weight:bold; color: {net_profit_color}">{formatted_net_profit}</div>'

                st.markdown("Net Profit", unsafe_allow_html=True)
                st.markdown(net_profit_display, unsafe_allow_html=True)

            st.markdown('<hr style="height:2px;border:none;color:#333;background-color:#333;" />', unsafe_allow_html=True)
            st.header("Revenue and Expenses by Type")

            revenue_breakdown_data = is_data_date_filtered.copy()
            revenue_breakdown_data['type'] = revenue_breakdown_data['account_name'].apply(extract_second_item)

            revenue_data = revenue_breakdown_data[revenue_breakdown_data['account_category'] == 'Income']
            grouped_revenues = revenue_data.groupby('type')['balance'].sum().reset_index()
            grouped_revenues['balance'] = grouped_revenues['balance'].abs()

            expense_breakdown_data = is_data_date_filtered.copy()
            expense_breakdown_data['type'] = expense_breakdown_data['account_name'].apply(extract_second_item)
            expense_data = expense_breakdown_data[expense_breakdown_data['account_category'] == 'Expense']
            grouped_expenses = expense_data.groupby('type')['balance'].sum().reset_index()
            grouped_expenses['balance'] = grouped_expenses['balance'].abs()

            # Add a select box to choose between Revenue and Expense breakdown
            selected_option = st.selectbox("Select a breakdown", ["Expenses", "Revenues"])

            if selected_option == "Revenues":
                fig = px.pie(grouped_revenues, names='type', values='balance', title="Revenues by Category", color='type', hole=0.3)
                st.plotly_chart(fig)
            else:
                fig = px.pie(grouped_expenses, names='type', values='balance', title="Expenses by Category", color='type', hole=0.3)
                st.plotly_chart(fig)

            st.markdown('<hr style="height:2px;border:none;color:#333;background-color:#333;" />', unsafe_allow_html=True)
            charts_df = is_data_date_filtered.copy()
            charts_df['month'] = pd.to_datetime(charts_df['accounting_period_ending']).dt.month_name()
            charts_df['balance'] = charts_df['balance'].apply(lambda x: abs(float(x)))
            charts_df['month_num'] = pd.to_datetime(charts_df['accounting_period_ending']).dt.month
            charts_df['month_name'] = pd.to_datetime(charts_df['accounting_period_ending']).dt.month_name()

            # Filter for COGS and Income
            cogs_data = charts_df[charts_df['account_type_name'] == 'Cost of Goods Sold']
            income_data = charts_df[charts_df['account_category'] == 'Income']


            # Group by month_name and month_num and aggregate by sum for balance and min for month_num
            cogs_grouped = cogs_data.groupby(['month_name', 'month_num'])['balance'].sum().reset_index(name='COGS')
            income_grouped = income_data.groupby(['month_name', 'month_num'])['balance'].sum().reset_index(name='Income')

            # Merge the two dataframes on month_name and month_num
            merged_df = pd.merge(income_grouped, cogs_grouped, on=['month_name', 'month_num'])

            # Sort the merged_df by month_num to ensure months are in order
            merged_df.sort_values('month_num', inplace=True)

            st.subheader("Monthly Revenue vs COGS")
            # Create the bar chart using 'month_name' for the x-axis
            fig = px.bar(merged_df, x='month_name', y=['Income', 'COGS'], 
                        labels={'value': 'Amount ($)', 'month_name': 'Month'},
                        barmode='group')

            st.plotly_chart(fig)

            st.markdown('<hr style="height:2px;border:none;color:#333;background-color:#333;" />', unsafe_allow_html=True)

            ### Cash Viz
            cash_data = bs_data_date_filtered.copy()

            # Convert accounting_period_ending to datetime
            cash_data['accounting_period_ending'] = pd.to_datetime(cash_data['accounting_period_ending'])

            # Filter rows that contain "Cash and Cash Equivalents" in the account_name
            cash_data = cash_data[cash_data['account_name'].str.lower().str.contains('cash and cash equivalents')]

            # Convert balance column to float
            cash_data['balance'] = cash_data['balance'].astype(float)

            # Group by accounting_period_ending and sum balances
            cash_per_period = cash_data.groupby('accounting_period_ending')['balance'].sum().reset_index()

            # Compute y-axis bounds with some buffer
            y_max = cash_per_period['balance'].max() * 1.1  # 10% above the max
            y_min = cash_per_period['balance'].min() * 0.9  # 10% below the min

            # Create a plotly line chart
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=cash_per_period['accounting_period_ending'], 
                                    y=cash_per_period['balance'],
                                    mode='lines+markers',
                                    name='Cash Balance'))

            fig.update_layout(xaxis_title="Period Ending",
                            yaxis_title="Cash Balance",
                            yaxis=dict(range=[y_min, y_max]),
                            template="plotly_dark")
            st.subheader("Cash Balance by Period")
            st.plotly_chart(fig)
            st.markdown('<hr style="height:2px;border:none;color:#333;background-color:#333;" />', unsafe_allow_html=True)
            st.subheader("Ratios")

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric(label="Gross Profit Margin", value=f"{gross_profit_margin:.2f}%", delta=None)
            with col2:
                st.metric(label="OpEx Ratio", value=f"{opex_ratio:.2%}")
            with col3:
                st.metric(label="Operating Profit Margin", value=f"{operating_profit_margin:.2f}%", delta=None)
            with col4:
                st.metric(label="Net Profit Margin", value=f"{net_profit_margin:.2f}%", delta=None)

            st.markdown('---')

            ## Ratios
            col3, col4, col5 = st.columns(3)
            # Compute the Ratios
            current_ratio = current_assets / current_liabilities if current_liabilities != 0 else 0
            quick_ratio = (current_assets - inventory) / current_liabilities if current_liabilities != 0 else 0
            liquid_assets = latest_cash_data['balance'].astype(float).sum()
            liquidity_ratio = liquid_assets / current_liabilities if current_liabilities != 0 else 0
            
            with col3:
                formatted_current_ratio = "{:,.2f}%".format(current_ratio)
                st.metric("Current Ratio", formatted_current_ratio, delta=None, delta_color="normal", help=None, label_visibility="visible")
            with col4:
                formatted_quick_ratio = "{:,.2f}%".format(quick_ratio)
                st.metric("Quick Ratio", formatted_quick_ratio, delta=None, delta_color="normal", help=None, label_visibility="visible")
            with col5:
                formatted_liquidity_ratio = "{:,.2f}%".format(liquidity_ratio)
                st.metric("Liquidity Ratio", formatted_liquidity_ratio, delta=None, delta_color="normal", help=None, label_visibility="visible")
        else:
            st.warning("Please ensure your starting period is before your ending period.")
