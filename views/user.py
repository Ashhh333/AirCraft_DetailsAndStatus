import streamlit as st
from database_connection import connect_to_database
from AdminControl.Operations import*
def user_view():
    mydb = connect_to_database()
    if mydb:
        tables = get_all_tables(mydb)
        # ... (rest of your existing view data code)
        if tables:
            selected_table = st.selectbox("Select a table to view:", tables)
            if selected_table:
                df = get_table_data(mydb, selected_table)
                if df is not None:
                    st.subheader(f"Data from table: {selected_table}")
                    st.dataframe(df)
                    
                    # Add download button
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="Download table as CSV",
                        data=csv,
                        file_name=f"{selected_table}.csv",
                        mime="text/csv"
                    )
                    
                    # Display table information
                    st.subheader("Table Information")
                    st.write(f"Number of Rows: {len(df)}")
                    st.write(f"Number of columns: {len(df.columns)}")
                    st.write("Column names:", ", ".join(df.columns))
        mydb.close()
