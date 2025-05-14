# Fivetran Netsuite Streamlit App
## 📣 Overview

The [Fivetran Netsuite Streamlit app](https://fivetran-netsuite.streamlit.app/) leverages data from the Fivetran Netsuite connector and Fivetran Netsuite data model to produce analytics ready reports. You may find the analytics ready reports within the pages of this Streamlit app (these may be found on the left pane). These dashboards have been constructed using a combination of the [netsuite2__balance_sheet](https://fivetran.github.io/dbt_netsuite/#!/model/model.netsuite2.netsuite2__balance_sheet) and [netsuite2__income_statement](https://fivetran.github.io/dbt_netsuite/#!/model/model.netsuite2.netsuite2__income_statement) models from the Fivetran [Netsuite dbt package](https://github.com/fivetran/dbt_netsuite). These dashboards provide an example of how you may analyze your Netsuite data.

By default this Streamlit app uses sample Dunder Mifflin Netsuite tickets data to generate the dashboards. This sample data is a replica of the `netsuite2__balance_sheet` and `netsuite2__income_statement` data model outputs. If you would like to leverage this app with your own data, you may follow the instructions within the below Installation and Deployment section.

## 📈 Provided reports

| **Page** | **Description** |
|----------|-----------------|
| [Financial Executive Dashboard](https://fivetran-netsuite.streamlit.app/financial_executive_dashboard) | This report is intended to serve as the executive dashboard for your company's financial well being. Based on the date range applied you will be able to view your company's high level balances, ratios, and revenue/expense breakdowns. Use this dashboard to keep track of your financial health and how you are trending. |
| [Balance Sheet Report](https://fivetran-netsuite.streamlit.app/balance_sheet_report) | This is a replica of your balance sheets for the date range applied. Inspect your assets, liabilities, and equity balances for the specified periods. This dashboard is intended to recreate the balance sheet report from Netsuite. | 
| [Income Statement Report](https://fivetran-netsuite.streamlit.app/profit_and_loss_report) | This is a replica of your cumulative income statement for the date range applied. Inspect your revenue and expenses for the specified periods. This dashboard is intended to recreate the income statement report from Netsuite. | 

## 🎯 Call to Action
These reports are designed to demonstrate the analytical capabilities when using the Fivetran Netsuite connector paired with the corresponding Netsuite data model. We encourage you to explore these reports and provide feedback. If you find these examples useful or have suggestions for additional content, please share your thoughts via a [GitHub issue](https://github.com/fivetran/streamlit_netsuite/issues/new). 
