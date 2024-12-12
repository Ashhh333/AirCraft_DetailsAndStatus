
import mysql.connector
import pandas as pd
import streamlit as st
def schedule_flight_and_manage_crew(connection, flight_data=None, action="insert"):
    try:
        cursor = connection.cursor()

        if action == "insert":
            # Step 1: Insert the flight
            st.write("Inserting flight record...")
            cursor.execute('''
                INSERT INTO Flights (FlightID, AircraftID, FlightNumber, DepartureAirport, ArrivalAirport, DepartureTime, ArrivalTime)
                VALUES (%s, %s, %s, %s, %s, %s, %s);
            ''', (
                flight_data['FlightID'], 
                flight_data['AircraftID'], 
                flight_data['FlightNumber'], 
                flight_data['DepartureAirport'], 
                flight_data['ArrivalAirport'], 
                flight_data['DepartureTime'], 
                flight_data['ArrivalTime']
            ))
            st.write("Flight record inserted!")

            # Step 2: Find and assign available crew members
            roles = ['Pilot', 'Co-Pilot', 'Flight Attendant']
            assigned_crew = {}

            for role in roles:
                st.write(f"Assigning crew for role: {role}")
                cursor.execute('''
                    SELECT c.CrewID
                    FROM Crew c
                    WHERE c.Role = %s
                      AND NOT EXISTS (
                          SELECT 1
                          FROM CrewAssignment ca
                          JOIN Flights f ON ca.FlightID = f.FlightID
                          WHERE ca.CrewID = c.CrewID
                            AND (
                                %s < f.ArrivalTime AND %s > f.DepartureTime
                            )
                      )
                    LIMIT 1;
                ''', (role, flight_data['DepartureTime'], flight_data['ArrivalTime']))

                result = cursor.fetchone()
                if result:
                    assigned_crew[role] = result[0]
                else:
                    raise Exception(f"No available crew member found for role: {role}")

            # Step 3: Assign crew to the flight
            for role, crew_id in assigned_crew.items():
                st.write(f"Assigning {role} with CrewID {crew_id} to FlightID {flight_data['FlightID']}")
                cursor.execute('''
                    INSERT INTO CrewAssignment (CrewID, FlightID, AssignedAircraftID)
                    VALUES (%s, %s, %s);
                ''', (crew_id, flight_data['FlightID'], flight_data['AircraftID']))

            connection.commit()
            st.success("Flight scheduled and crew assigned successfully!")

        elif action == "update":
            # Update flight details
            st.write("Updating flight record...")
            cursor.execute('''
                UPDATE Flights
                SET AircraftID = %s, FlightNumber = %s, DepartureAirport = %s, ArrivalAirport = %s,
                    DepartureTime = %s, ArrivalTime = %s
                WHERE FlightID = %s;
            ''', (
                flight_data['AircraftID'], 
                flight_data['FlightNumber'], 
                flight_data['DepartureAirport'], 
                flight_data['ArrivalAirport'], 
                flight_data['DepartureTime'], 
                flight_data['ArrivalTime'],
                flight_data['FlightID']
            ))
            st.write("Flight record updated!")

            # Optional: Update crew assignment (if needed)
            st.info("You may need to reassign crew members if flight timings are changed.")
            # Logic for reassigning can be similar to the insert section

            connection.commit()
            st.success("Flight updated successfully!")

        elif action == "delete":
            # Step 1: Delete associated crew assignments
            st.write(f"Deleting crew assignments for FlightID {flight_data['FlightID']}...")
            cursor.execute('''
                DELETE FROM CrewAssignment
                WHERE FlightID = %s;
            ''', (flight_data['FlightID'],))
            st.write("Crew assignments deleted!")

            # Step 2: Delete the flight record
            st.write(f"Deleting flight record for FlightID {flight_data['FlightID']}...")
            cursor.execute('''
                DELETE FROM Flights
                WHERE FlightID = %s;
            ''', (flight_data['FlightID'],))
            st.write("Flight record deleted!")

            connection.commit()
            st.success("Flight and associated crew assignments deleted successfully!")

    except Exception as e:
        # Roll back the transaction in case of failure
        connection.rollback()
        st.error(f"Error during {action}: {str(e)}")

    finally:
        cursor.close()
