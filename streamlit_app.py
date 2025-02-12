import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static

def display_map():
    df = pd.read_csv('processed/processed.csv')
    amenity_columns = df.columns[17:]
    df["available_amenities"] = df[amenity_columns].apply(
        lambda row: {col: row[col] for col in amenity_columns if pd.notna(row[col]) and str(row[col]).strip().lower() not in ["n", "no", "0", "false", "y", "yes", "1", "true"]},
        axis=1
    )
    df["amenities_str"] = df["available_amenities"].apply(lambda x: "<br>".join(f"{k}: {v}" for k, v in x.items()) if x else "No amenities available")
    df["clean_stop_name"] = df["stop_name"].apply(lambda x: x.split('#')[0].strip())
    unique_stop_names = df["clean_stop_name"].unique()

    st.set_page_config(page_title="Fuel Stops Map", layout="wide")
    st.title("Fuel Stops Map with Filters and Details")

    st.sidebar.header("Filter Options")
    selected_stops = st.sidebar.selectbox("Select Stop Name", ["All"] + list(unique_stop_names))
    selected_amenities = st.sidebar.multiselect("Select Amenities", amenity_columns)

    filtered_df = df if selected_stops == "All" else df[df["clean_stop_name"] == selected_stops]
    if selected_amenities:
        filtered_df = filtered_df[filtered_df["available_amenities"].apply(lambda x: any(amenity in x for amenity in selected_amenities))]

    m = folium.Map(location=[df["latitude"].mean(), df["longitude"].mean()], zoom_start=5)

    for _, row in filtered_df.iterrows():
        folium.Marker(
            location=[row["latitude"], row["longitude"]],
            popup=folium.Popup(f"<b>{row['stop_name']}</b><br>"
                               f"Latitude: {row['latitude']}<br>"
                               f"Longitude: {row['longitude']}<br>"
                               f"Fuel Diesel Price: {row.get('fuel_diesel_price', 'N/A')}<br>"
                               f"<b>Amenities:</b><br>{row['amenities_str']}", max_width=250),
            icon=folium.Icon(color='red')
        ).add_to(m)

    folium_static(m)

if __name__ == '__main__':
    display_map()