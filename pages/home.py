import streamlit as st
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import base64
import warnings

st.logo("images/lavenir.PNG")

def get_base64(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# Set background image
def set_background(png_file):
    bin_str = get_base64(png_file)
    page_bg_img = '''
    <style>
    .stApp {
    background-image: url("data:image/png;base64,%s");
    background-size: cover;
    }
    </style>
    ''' % bin_str
    st.markdown(page_bg_img, unsafe_allow_html=True)

def show_dashboard():
    # Ignore all warnings
    warnings.filterwarnings("ignore")   
    
    set_background('./images/background.png')

    st.title("L'Avenir Holdings inc Dashboard")

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["HOME", "VIEW", "HISTORY", "2024 PREDICTED BUYERS", "SETTINGS", "ABOUT"])

    @st.cache_data
    def load_data(file):
        return pd.read_excel(file)

    @st.cache_data
    def filter_data(dataa, year_range, price, buyer, owner_column, neighborhood_column):
        if isinstance(buyer, str):
            buyer = [buyer]
        filtered_data = dataa[(dataa['Prior Sale Year'].isin(range(year_range[0], year_range[1] + 1))) & 
                              (dataa[neighborhood_column].isin(range(price[0], price[1] + 1))) & 
                              (dataa[owner_column].isin(buyer))]
        return filtered_data

    @st.cache_data
    def filter_data_based_on_price(dataa, price, neighborhood_column):
        filtered_data = dataa[(dataa[neighborhood_column].isin(range(price[0], price[1] + 1)))]
        return filtered_data

    @st.cache_data
    def filter_data_based_on_county(dataa, county):
        filtered_data = dataa[(dataa["Situs City"].isin(county))]
        return filtered_data

    @st.cache_data
    def filter_data_based_on_year(dataa, year_range):
        filtered_data = dataa[(dataa['Prior Sale Year'].isin(range(year_range[0], year_range[1] + 1)))]
        return filtered_data

    @st.cache_data
    def get_slider_ranges(data, column_name):
        numeric_data = pd.to_numeric(data[column_name], errors='coerce').dropna()
        if numeric_data.empty:
            return (0, 0)
        min_value = numeric_data.min()
        max_value = numeric_data.max()
        return (int(min_value), int(max_value))

    # st.image("images/lavenir.PNG")
    # Initialize session state for data file selection
    if 'data_file' not in st.session_state:
        st.session_state['data_file'] = 'merged_df.xlsx'

    # Initial data load
    data = load_data(st.session_state['data_file'])

    # Determine the column names based on the data file
    if st.session_state['data_file'] == 'merged_df.xlsx':
        owner_column = 'Owner 1'
        neighborhood_column = 'Neighborhood'
    else:
        owner_column = 'Owner'
        neighborhood_column = 'Situs City'
    
    def update_property_type(selected):
        st.session_state.property_type = selected

    def update_vehicle_type(selected):
        st.session_state.vehicle_type = selected

    # Function to clean and convert numeric columns
    def clean_numeric_column(series):
        series = series.apply(lambda x: str(x).split(',')[0].strip())
        series = pd.to_numeric(series, errors='coerce')
        return series

    # Function to clean and convert coordinate columns
    def clean_coordinate_column(series):
        series = series.apply(lambda x: str(x).split(',')[0].strip())
        series = pd.to_numeric(series, errors='coerce')
        return series

    # Initialize session state for checkboxes
    if 'property_type' not in st.session_state:
        st.session_state.property_type = None

    # Initialize session state for checkboxes
    if 'vehicle_type' not in st.session_state:
        st.session_state.vehicle_type = None

    @st.cache_data
    def filter_data_based_on_type(data):
        filtered_data = data[(data['Type'].isin(['IND', 'CORP']))]
        return filtered_data
    
    with tab1:
        col1, col2 = st.columns(2)
        # tab1_data = load_data('all_2024_details.xlsx')
        # tab1_data = filter_data_based_on_type(tab1_data)

        with col1:
            state = ["Alabama(AL)", "Alaska(AK)", "Arizona(AZ)", "Arkansas(AR)", "California(CA)", "Colorado(CO)", "Connecticut(CT)", "Delaware(DE)", "Florida(FL)", "Georgia(GA)", "Hawaii(HI)", "Idaho(ID)", "Illinois(IL)", "Indiana(IN)", "Iowa(IA)", "Kansas(KS)", "Kentucky(KY)", "Louisiana(LA)", "Maine(ME)", "Maryland(MD)", "Massachusetts(MA)", "Michigan(MI)", "Minnesota(MN)", "Mississippi(MS)", "Missouri(MO)", "Montana(MT)", "Nebraska(NE)", "Nevada(NV)", "New Hampshire(NH)", "New Jersey(NJ)", "New Mexico(NM)", "New York(NY)", "North Carolina(NC)", "North Dakota(ND)", "Ohio(OH)", "Oklahoma(OK)", "Oregon(OR)", "Pennsylvania(PA)", "Rhode Island(RI)", "South Carolina(SC)", "South Dakota(SD)", "Tennessee(TN)", "Texas(TX)", "Utah(UT)", "Vermont(VT)", "Virginia(VA)", "Washington(WA)", "West Virginia(WV)", "Wisconsin(WI)", "Wyoming(WY)"]
            selected_state = st.selectbox('State', ['All'] + state)

        if selected_state == "Florida(FL)":
            with col2:
                county = data["Situs City"].unique().tolist()
                selected_county = st.selectbox('County/Township', ['All'] + county)
                
                property_type = st.radio("Select Property Type:", ["None", "Properties", "Vehicle", "Valuable Goods"], key='property_type', horizontal=False, index=0)
            
            if property_type == "Properties":
                st.write("Select the type of Properties")
                selected_property_subtype = st.radio("Subtype", ["Corporation", "Residential", "Individual"], key='property_subtype')

                if st.button("Load Data"):
                    filtered_data = filter_data_based_on_county(data, [selected_county])
                    if selected_property_subtype == "Corporation":
                        filtered_data = filtered_data[filtered_data["Type"] == "CORP"]
                    elif selected_property_subtype == "Individual":
                        filtered_data = filtered_data[filtered_data["Type"] == "IND"]
                    elif selected_property_subtype == "Residential":
                        filtered_data = filtered_data[filtered_data["Type"] == "IND"]
                    st.success("Data Loaded below..")
                    st.dataframe(filtered_data, width=1000, height=600)
                else:
                    st.warning("Select option from above..")

            elif property_type == "Vehicle":
                st.write("Select the type of Vehicle")
                selected_vehicle_subtype = st.radio("Subtype", ["Individual Vehicle", "Commercial Vehicle"], key='vehicle_subtype')
                if selected_vehicle_subtype:
                    st.success(f"You chose {selected_vehicle_subtype} to filter data")
                    if st.button("Load Data"):
                        filtered_data = filter_data_based_on_county(data, [selected_county])
                        st.warning("No Data available for Vehicles..")
                        # st.dataframe(filtered_data, width=1000, height=600)
                    else:
                        st.warning("Select option from above..")

            elif property_type == "Valuable Goods":
                st.success("You chose Valuable Goods to filter data")
                if st.button("Load Data"):
                    filtered_data = filter_data_based_on_county(data, [selected_county])
                    st.success("No Available option for Valuable goods..")
                    # st.dataframe(filtered_data, width=1000, height=600)
                else:
                    st.warning("Select option from above..")

    with tab2:
        data = data.dropna(subset=['lat', 'lng', 'Situs Zip Code', 'Last Sale Date', 'Prior Sale Date', 'Year Built'])
        
        # Clean date strings before converting to datetime
        data['Last Sale Date'] = data['Last Sale Date'].apply(lambda x: str(x).split(',')[0].strip())
        data['Prior Sale Date'] = data['Prior Sale Date'].apply(lambda x: str(x).split(',')[0].strip())
        
        data['Last Sale Date'] = pd.to_datetime(data['Last Sale Date'], format='%m/%d/%Y', errors='coerce')
        data['Prior Sale Date'] = pd.to_datetime(data['Prior Sale Date'], format='%m/%d/%Y', errors='coerce')
        
        data['Last Sale Year'] = data['Last Sale Date'].dt.year
        data['Prior Sale Year'] = data['Prior Sale Date'].dt.year

        # Clean and convert numeric columns
        data['Year Built'] = clean_numeric_column(data['Year Built'])

        # Clean and convert coordinate columns
        data['lat'] = clean_coordinate_column(data['lat'])
        data['lng'] = clean_coordinate_column(data['lng'])
        
        data = data.sample(frac=0.1, random_state=10)

        geometry = [Point(xy) for xy in zip(data['lng'], data['lat'])]
        gdf = gpd.GeoDataFrame(data, geometry=geometry, crs="EPSG:4326")

        st.subheader("Original map:")
        st.map(gdf.rename(columns={'lng': 'longitude', 'lat': 'latitude'}), zoom=8)

        year_min = min(data['Last Sale Year'].min(), data['Prior Sale Year'].min(), data['Year Built'].min())
        year_max = max(data['Last Sale Year'].max(), data['Prior Sale Year'].max(), data['Year Built'].max())

        col1, col2 = st.columns(2)

        with col1:
            selected_year = st.slider('Year', 2000, 2024, (2000, 2024))
            buyers = data[owner_column].unique().tolist()
            selected_buyer = st.selectbox('Buyer', ['All'] + buyers)

        with col2:
            min_price, max_price = get_slider_ranges(data, 'Last Sale Amount')
            selected_price = st.slider('Price', 1000, 10000, (1000, 10000))
            neighborhoods = data[neighborhood_column].unique().tolist()
            selected_neighborhood = st.selectbox(neighborhood_column, ['All'] + neighborhoods)

        filtered_data = filter_data(data, selected_year, selected_price, selected_buyer, owner_column, neighborhood_column)
        geometry_filtered = [Point(xy) for xy in zip(filtered_data['lng'], filtered_data['lat'])]
        gdf_filtered = gpd.GeoDataFrame(filtered_data, geometry=geometry_filtered, crs="EPSG:4326")

        st.subheader("Filtered map:")
        st.map(gdf_filtered.rename(columns={'lng': 'longitude', 'lat': 'latitude'}), zoom=8)

        if selected_buyer != 'All':
            filtered_data = filtered_data[filtered_data[owner_column] == selected_buyer]

        st.title('Selected Price Range')
        st.write(f'Min Price: {selected_price[0]:,} - Max Price: {selected_price[1]:,}')

        st.title('Filtered Data')
        st.dataframe(filtered_data.T, width=1000, height=600)

    with tab3:
        st.subheader("What do you want to search today?")
        filter_options = ["Buyers", "Years", "Price", neighborhood_column]
        selected_filter = st.radio("Select a filter option:", filter_options, horizontal=True)
        display_data = False
        filtered_data = data  # Initializing `filtered_data` with the entire dataset

        if selected_filter == "Buyers":
            buyers_predict = data[owner_column].unique().tolist()
            selected_buyer_predict = st.selectbox('Buyers', ['All'] + buyers_predict)
            if selected_buyer_predict != 'All':
                filtered_data = filtered_data[filtered_data[owner_column] == selected_buyer_predict]
            display_data = True

        elif selected_filter == "Years":
            year_min, year_max = get_slider_ranges(data, 'Last Sale Year')
            selected_year_predict = st.slider('Years', year_min, year_max, (year_min, year_max))
            filtered_data = filter_data_based_on_year(data, selected_year_predict)
            display_data = True

        elif selected_filter == "Price":
            min_price, max_price = get_slider_ranges(data, 'Last Sale Amount')
            selected_price_predict = st.slider('Prices', min_price, max_price, (min_price, max_price))
            filtered_data = filter_data_based_on_price(data, selected_price_predict, neighborhood_column)
            display_data = True

        elif selected_filter == neighborhood_column:
            neighborhoods = data[neighborhood_column].unique().tolist()
            selected_neighborhood_predict = st.selectbox('Neighborhoods', ['All'] + neighborhoods)
            if selected_neighborhood_predict != 'All':
                filtered_data = filtered_data[filtered_data[neighborhood_column] == selected_neighborhood_predict]
            display_data = True

        if display_data:
            st.title('Filtered Data')
            st.dataframe(filtered_data.T, width=1000, height=600)

    with tab4:
        st.subheader("Predicted Buyers for 2024")

        # if st.session_state['data_file'] != 'all_2024_details.xlsx':
        #     st.warning("Please switch to the reduced data file in the Settings tab to use this feature.")
        # else:
        reduced_data = load_data('all_2024_details.xlsx')

        owners = reduced_data['Owner'].unique().tolist() if 'Owner' in reduced_data.columns else []
        types = reduced_data['Type'].dropna().unique().tolist() if 'Type' in reduced_data.columns else []

        selected_owner = st.selectbox('Owner', ['All'] + owners)
        selected_type = st.selectbox('Type', ['All'] + types)

        if 'Owner' in reduced_data.columns and 'Type' in reduced_data.columns:
            if selected_owner != 'All':
                reduced_data = reduced_data[reduced_data['Owner'] == selected_owner]
            if selected_type != 'All':
                reduced_data = reduced_data[reduced_data['Type'] == selected_type]

            st.title('Filtered Data')

            # Check if both owner and type are "All"
            if selected_owner == 'All' and selected_type == 'All':
                st.warning("Please select to see predicted buyers")  # Display all data
            else:
                if reduced_data.shape[0] == 1:
                    # Display the map and data vertically
                    row = reduced_data.iloc[0]
                    latitude = float(row['lat'].split(',')[0].strip())  # Extract latitude and convert to float
                    longitude = float(row['lng'].split(',')[0].strip())  # Extract longitude and convert to float
                    map_data = pd.DataFrame([[latitude, longitude]], columns=['latitude', 'longitude'])
                    st.map(map_data, zoom=8)
                    st.dataframe(row, width=1000, height=600)
                else:
                    # Display the data horizontally
                    for index, row in reduced_data.iterrows():
                        pcol1, pcol2 = st.columns(2)
                        with pcol1:
                            # Display the map
                            latitude = float(row['lat'].split(',')[0].strip())  # Extract latitude and convert to float
                            longitude = float(row['lng'].split(',')[0].strip())  # Extract longitude and convert to float
                            map_data = pd.DataFrame([[latitude, longitude]], columns=['latitude', 'longitude'])
                            st.map(map_data, zoom=8)
                            
                        with pcol2:
                            st.dataframe(row, width=600, height=400)

    with tab5:
        st.header("Settings")
        st.subheader('What type of data do you want to use to filter?')
        
        col1, col2 = st.columns(2)
        data_selected = None
        
        with col1:
            if st.button('Select Large Data'):
                st.session_state['data_file'] = 'merged_df.xlsx'
                st.session_state['data_selected'] = 'Large Data Selected'
                st.rerun()
        
        with col2:
            if st.button('Select Reduced Data'):
                st.session_state['data_file'] = 'all_2024_details.xlsx'
                st.session_state['data_selected'] = 'Reduced Data Selected'
                st.rerun()
        
        if 'data_selected' in st.session_state:
            st.success(st.session_state['data_selected'])

    with tab6:
        # st.header("About us")
        st.image("images/lavenir.PNG")
        st.write("L'Avenir Holdings Inc. stands as a beacon in the real estate landscape of Sarasota, Florida, USA. Specializing in the art of property transactions, our expertise spans the spectrum from sprawling lands to cozy apartments, from charming townhouses to luxurious waterfront retreats. \n\nOur dedication lies in crafting seamless experiences for both buyers and sellers, ensuring every transaction is not just a deal, but a journey towards realizing dreams and aspirations. With an unwavering commitment to excellence, we navigate the complexities of the real estate market with finesse, guided by a vision of shaping tomorrow's landscapes today. \n\nAt L'Avenir Holdings Inc., every property is not just a structure; it's a canvas waiting to be adorned with memories and possibilities. Whether it's finding the perfect home to settle into or unlocking the potential of a lucrative investment opportunity, we are the trusted partner guiding you every step of the way. With integrity, innovation, and a passion for the extraordinary, we redefine what it means to turn dreams into reality in the realm of real estate.")

# Check if the user is authenticated
if __name__ == "__main__":
    if 'authenticated' in st.session_state and st.session_state.authenticated:
        show_dashboard()
    else:
        show_dashboard()
        st.rerun()  # Redirect to main.py for login
