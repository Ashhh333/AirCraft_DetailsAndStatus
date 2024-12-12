from database_connection import connect_to_database
import pandas as pd

def manufacturer_dashboard():
    st.subheader("Manufacturer Dashboard")
    st.write(f"Welcome, {st.session_state.username}!")

    # Dropdown menu for different options
    options = [
        "Flight Details",
        "Flight Crew",
        "Incidents",
        "Aircraft Status",
        "Maintenance Info",
    ]
    selected_option = st.selectbox("Select an option to view details:", options)

    # Establish database connection
    mydb = connect_to_database()
    if mydb:
        cursor = mydb.cursor(dictionary=True)

        # Handle each option
        if selected_option == "Flight Details":
            query = """
                SELECT 
                    a.AircraftID, 
                    a.Model, 
                    a.Capacity, 
                    a.FlightRange, 
                    f.FlightNumber, 
                    f.DepartureAirport, 
                    f.ArrivalAirport, 
                    f.DepartureTime, 
                    f.ArrivalTime
                FROM Aircraft a
                JOIN Flights f ON a.AircraftID = f.AircraftID
                WHERE a.Manufacturer = %s
            """
            cursor.execute(query, (st.session_state.username,))
            data = cursor.fetchall()

        elif selected_option == "Flight Crew":
            query = """
                SELECT 
                    c.AssignedAircraftID AS AircraftID, 
                    c.CrewID, 
                    cr.Name, 
                    cr.Role
                FROM CrewAssignment c
                JOIN Crew cr ON c.CrewID = cr.CrewID
                JOIN Aircraft a ON c.AssignedAircraftID = a.AircraftID
                WHERE a.Manufacturer = %s
            """
            cursor.execute(query, (st.session_state.username,))
            data = cursor.fetchall()

        elif selected_option == "Incidents":
            query = """
                SELECT 
                    i.AircraftID, 
                    i.IncidentID, 
                    d.Description, 
                    i.Severity
                FROM IncidentInfo i
                JOIN IncidentDetails d ON i.IncidentID = d.IncidentID
                JOIN Aircraft a ON i.AircraftID = a.AircraftID
                WHERE a.Manufacturer = %s
            """
            cursor.execute(query, (st.session_state.username,))
            data = cursor.fetchall()

        elif selected_option == "Aircraft Status":
            query = """
                SELECT 
                    s.AircraftID, 
                    s.StatusID, 
                    s.Status, 
                    s.StatusDate
                FROM AircraftStatus s
                JOIN Aircraft a ON s.AircraftID = a.AircraftID
                WHERE a.Manufacturer = %s
            """
            cursor.execute(query, (st.session_state.username,))
            data = cursor.fetchall()

        elif selected_option == "Maintenance Info":
            query = """
                SELECT 
                    m.AircraftID, 
                    m.MaintenanceID, 
                    m.MaintenanceType, 
                    m.StartDate, 
                    m.EndDate, 
                    t.TeamName
                FROM MaintenanceInfo m
                JOIN MaintenanceAssignment ma ON m.MaintenanceID = ma.MaintenanceID
                JOIN MaintenanceTeam t ON ma.TeamID = t.TeamID
                JOIN Aircraft a ON m.AircraftID = a.AircraftID
                WHERE a.Manufacturer = %s
            """
            cursor.execute(query, (st.session_state.username,))
            data = cursor.fetchall()

        else:
            data = None

        # Display results
        if data:
            st.dataframe(data)
            csv = pd.DataFrame(data).to_csv(index=False)
            st.download_button(
                label="Download data as CSV",
                data=csv,
                file_name=f"{selected_option.replace(' ', '_').lower()}_data.csv",
                mime="text/csv"
            )
        else:
            st.warning(f"No data found for {selected_option}.")

        # Close database connection
        cursor.close()
        mydb.close()
    else:
        st.error("Failed to connect to the database.")

import streamlit as st