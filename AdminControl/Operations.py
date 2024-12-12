import mysql.connector
import pandas as pd
import streamlit as st
from AdminControl.Transaction import *


def get_all_tables(mydb):
    try:
        with mydb.cursor() as cursor:
            cursor.execute("SHOW TABLES")
            tables = [table[0] for table in cursor.fetchall() if table[0] != 'users']
        return tables 
    
    except mysql.connector.Error as e:
        st.error(f"Error fetching tables: {e}")
        return []

def get_table_data(mydb,tablename):
    try:
        query=f"SELECT * FROM {tablename}"
        df=pd.read_sql(query,mydb)
        return df
    except mysql.connector.Error as e:
        st.error(f"Error fetching data from table {tablename}: {e}")
        return None

def table_operations(connection):
    st.header("Table Operations")
    
    # Fetch all table names
    tables = get_all_tables(connection)
    selected_table = st.selectbox("Select Table", tables)
    
    if selected_table:
        operation = st.radio("Select Operation", ["View", "Insert", "Update", "Delete"])
        
        if operation == "View":
            df = get_table_data(connection, selected_table)
            if df is not None:
                st.dataframe(df)
        
        elif operation == "Insert":
            st.subheader(f"Insert into {selected_table}")
            
            if selected_table == "Flights":
                # Input fields for Flights
                flight_id = st.text_input("Enter Flight ID")
                aircraft_id = st.number_input("Enter Aircraft ID", step=1)
                flight_number = st.text_input("Enter Flight Number")
                departure_airport = st.text_input("Enter Departure Airport")
                arrival_airport = st.text_input("Enter Arrival Airport")
                departure_time = st.text_input("Enter Departure Time (Format: YYYY-MM-DD HH:MM:SS)")
                arrival_time = st.text_input("Enter Arrival Time (Format: YYYY-MM-DD HH:MM:SS)")
                
                if st.button("Insert Record"):
                    try:
                        # Prepare flight data
                        flight_data = {
                            'FlightID': flight_id,
                            'AircraftID': aircraft_id,
                            'FlightNumber': flight_number,
                            'DepartureAirport': departure_airport,
                            'ArrivalAirport': arrival_airport,
                            'DepartureTime': departure_time,
                            'ArrivalTime': arrival_time
                        }
                        
                        # Schedule flight and assign crew
                        schedule_flight_and_manage_crew(connection,flight_data)
                    except mysql.connector.Error as e:
                        if "Duplicate entry" in str(e):
                            st.error("Same flight is going somewhere else at the entered time.")
                        else:
                            st.error(f"Error inserting record: {e}")
            else:
                # Generic Insert for other tables
                cursor = connection.cursor()
                cursor.execute(f"DESCRIBE {selected_table}")
                columns = cursor.fetchall()
                cursor.close()
                
                values = {}
                for col in columns:
                    col_name = col[0]
                    col_type = col[1]
                    if col_name not in ['id', 'created_at']:  # Skip auto-generated columns
                        if 'int' in col_type:
                            values[col_name] = st.number_input(f"Enter {col_name}", step=1)
                        elif 'float' in col_type or 'double' in col_type:
                            values[col_name] = st.number_input(f"Enter {col_name}", step=0.01)
                        else:
                            values[col_name] = st.text_input(f"Enter {col_name}")
                
                if st.button("Insert Record"):
                    try:
                        cursor = connection.cursor()
                        cols = ', '.join(values.keys())
                        vals = ', '.join(['%s'] * len(values))
                        query = f"INSERT INTO {selected_table} ({cols}) VALUES ({vals})"
                        cursor.execute(query, list(values.values()))
                        connection.commit()
                        cursor.close()
                        st.success("Record inserted successfully!")
                    except mysql.connector.Error as e:
                        st.error(f"Error inserting record: {e}")
        
        elif operation == "Update":
                df = get_table_data(connection, selected_table)
                
                if df is not None:
                    st.dataframe(df)
                    
                    # Get primary key for the table
                    cursor = connection.cursor()
                    cursor.execute(f"SHOW KEYS FROM {selected_table} WHERE Key_name = 'PRIMARY'")
                    primary_key = cursor.fetchone()[4]  # Column name of primary key
                    
                    # Select record to update
                    record_id = st.number_input(f"Enter {primary_key} of record to update", min_value=1)
                    
                    # Get column names and types
                    cursor.execute(f"DESCRIBE {selected_table}")
                    columns = cursor.fetchall()
                    cursor.close()
                    
                    # Create input fields for each column
                    values = {}
                    for col in columns:
                        col_name = col[0]
                        col_type = col[1]
                        if col_name not in ['id', 'created_at', primary_key]:  # Skip primary key and auto-generated columns
                            if 'int' in col_type:
                                values[col_name] = st.number_input(f"New value for {col_name}", step=1)
                            elif 'float' in col_type or 'double' in col_type:
                                values[col_name] = st.number_input(f"New value for {col_name}", step=0.01)
                            else:
                                values[col_name] = st.text_input(f"New value for {col_name}")
                    
                    if st.button("Update Record"):
                        try:
                            cursor = connection.cursor()
                            set_clause = ', '.join([f"{k} = %s" for k in values.keys()])
                            query = f"UPDATE {selected_table} SET {set_clause} WHERE {primary_key} = %s"
                            cursor.execute(query, list(values.values()) + [record_id])
                            connection.commit()
                            cursor.close()
                            st.success("Record updated successfully!")
                        except mysql.connector.Error as e:
                            st.error(f"Error updating record: {e}")


        
        elif operation == "Delete":
            df = get_table_data(connection, selected_table)
            if selected_table == "Flights":
                # Input field for FlightID (as only this is required for deletion)
                flight_id = st.text_input("Enter Flight ID to Delete")
                
                if st.button("Delete Record"):
                    try:
                        # Prepare flight data for deletion
                        if not flight_id:
                            st.error("Please enter a Flight ID.")
                            return

                        # Call the delete operation
                        flight_data = {'FlightID': flight_id}
                        schedule_flight_and_manage_crew(connection, flight_data, action="delete")
                        
                    except mysql.connector.Error as e:
                        st.error(f"Error during deletion: {e}")
                        
            if df is not None:
                st.dataframe(df)