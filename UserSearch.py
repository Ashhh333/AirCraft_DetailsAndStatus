import streamlit as st
from database_connection import connect_to_database


def get_airport_names(mydb):
    """
    Fetches a list of unique airport names (Departure and Arrival airports) from the Flights table.
    Joins with the Airports table to fetch full airport names.
    """
    try:
        cursor = mydb.cursor()
        query = """
        SELECT DISTINCT a.AirportName
        FROM Airports a
        JOIN Flights f ON f.DepartureAirport = a.IATACode
        UNION
        SELECT DISTINCT a.AirportName
        FROM Airports a
        JOIN Flights f ON f.ArrivalAirport = a.IATACode
        """
        cursor.execute(query)
        airports = [row[0] for row in cursor.fetchall()]
        cursor.close()
        return sorted(airports)  # Sort alphabetically for better UX
    except Exception as e:
        st.error(f"Error fetching airport names: {e}")
        return []


def flight_search_view():
    # Connect to the database
    mydb = connect_to_database()

    if mydb:
        st.title("Flight Search")

        # Fetch unique airport names
        airports = get_airport_names(mydb)

        if airports:
            # Input fields for filtering
            departure_airport = st.selectbox("Select Departure Airport (optional)", [""] + airports)
            arrival_airport = st.selectbox("Select Arrival Airport (optional)", [""] + airports)
        else:
            st.warning("No airports found in the database.")
            departure_airport, arrival_airport = None, None

        departure_date = st.date_input("Departure Date (optional)")
        arrival_date = st.date_input("Arrival Date (optional)")

        # Convert dates to strings
        departure_date = str(departure_date) if departure_date else None
        arrival_date = str(arrival_date) if arrival_date else None

        # Search button
        if st.button("Search Flights"):
            with st.spinner("Fetching flight data..."):
                df = filter_flights(
                    mydb,
                    departure_airport=departure_airport if departure_airport else None,
                    arrival_airport=arrival_airport if arrival_airport else None,
                    departure_date=departure_date,
                    arrival_date=arrival_date
                )

            if df is not None and not df.empty:
                st.success("Flights fetched successfully!")
                st.dataframe(df)

                # Download button for filtered data
                csv = df.to_csv(index=False)
                st.download_button(
                    label="Download results as CSV",
                    data=csv,
                    file_name="filtered_flights.csv",
                    mime="text/csv"
                )
            elif df is not None:
                st.warning("No flights match the given criteria.")

        mydb.close()

def filter_flights(mydb, departure_airport=None, arrival_airport=None, departure_date=None, arrival_date=None):
    """
    Fetches flights from the Flights table based on the provided filters.
    Uses airport names for filtering.
    """
    try:
        cursor = mydb.cursor(dictionary=True)

        query = """
        SELECT f.FlightNumber, f.DepartureAirport, f.ArrivalAirport, f.DepartureTime, f.ArrivalTime
        FROM Flights f
        JOIN Airports a1 ON f.DepartureAirport = a1.IATACode
        JOIN Airports a2 ON f.ArrivalAirport = a2.IATACode
        WHERE 1 = 1
        """
        params = []

        if departure_airport:
            query += " AND a1.AirportName = %s"
            params.append(departure_airport)

        if arrival_airport:
            query += " AND a2.AirportName = %s"
            params.append(arrival_airport)

        if departure_date:
            query += " AND DATE(f.DepartureTime) = %s"
            params.append(departure_date)

        if arrival_date:
            query += " AND DATE(f.ArrivalTime) = %s"
            params.append(arrival_date)

        cursor.execute(query, params)
        flights = cursor.fetchall()
        cursor.close()

        # Convert to DataFrame for better handling
        import pandas as pd
        return pd.DataFrame(flights)
    except Exception as e:
        st.error(f"Error filtering flights: {e}")
        return None