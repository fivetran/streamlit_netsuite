import streamlit as st

def destination_selection():
    destination_options = ['Dunder Mifflin Sample Data', 'BigQuery', 'Snowflake']
    default_index = destination_options.index('Dunder Mifflin Sample Data')
    if st.session_state.get("destination", "Dunder Mifflin Sample Data") == "Dunder Mifflin Sample Data":
        destination = st.sidebar.selectbox('Choose your destination:', destination_options, index=default_index)
    else:
        default_index = destination_options.index(st.session_state.get("destination"))
        destination = st.sidebar.selectbox('Choose your destination:', destination_options, index=default_index)
    st.session_state.destination = destination
    return destination

def database_schema_variables():
    if st.session_state.get("destination", "Dunder Mifflin Sample Data") != "Dunder Mifflin Sample Data":
        if st.session_state.get("database", "Database") == "Database":
            database = st.sidebar.text_input("Enter the name of your database:", "Database")
        else:
            database = st.session_state.get("database")
            database = st.sidebar.text_input("Enter the name of your database:", database)
        
        if st.session_state.get("database", "Schema") == "Schema":
            schema = st.sidebar.text_input("Enter the name of your schema:", "Schema")
        else:
            schema = st.session_state.get("schema")
            schema = st.sidebar.text_input("Enter the name of your schema:", schema)

        st.session_state.database = database
        st.session_state.schema = schema
    else:
        database = None
        st.session_state.database = database
        schema = None
        st.session_state.schema = schema

    return database, schema
