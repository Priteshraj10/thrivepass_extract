import streamlit as st
import pandas as pd
from PIL import Image
from datetime import datetime, date, timedelta
import os
import csv

image = Image.open('assets/tp logo day.png')
st.set_page_config(page_title='Ecolab COBRA',
                   page_icon=image, layout='wide')
st.image('assets/tp-wordmark-day.png', width=400)

uploaded_file = st.file_uploader("Choose a file")
if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)

    # create a function for new header for the dataframe
    def new_header(df):
        new_header = df.iloc[0]  # grab the first row for the header
        df = df[1:]  # take the data less the header row
        df.columns = new_header  # set the header row as the df header
        return df

    def check_age(date):
        born = datetime.strptime(str(date), "%Y-%m-%d %H:%M:%S").date()
        sixty_days = days_60 + timedelta(days=days_slider)
        return sixty_days.year - born.year - ((sixty_days.month, days_60.day) < (born.month, born.day))

    df = new_header(df)
    # str contains method
    mask = df[df['MemberID'].str.contains(r"MemberID", na=False)]

    # indexes of mask
    indexes = mask.index.values

    # member information dataframe
    member_df = df.iloc[0:indexes[0] - 3]

    # plan information dataframe
    plan_df = df.iloc[indexes[0] - 1:indexes[1] - 3]
    plan_df = new_header(plan_df)

    final_df = pd.merge(plan_df, member_df, on='MemberID', how='inner')

    # sort by memberid
    final_df = final_df.sort_values(by=['MemberID'])

    final_df.columns = final_df.columns.fillna('to_drop')
    final_df.drop('to_drop', axis=1, inplace=True)
    final_df = final_df.astype(str)

    # function pandas datatime
    def pandas_datatime(df):
        df['DOB'] = pd.to_datetime(df['DOB'], format='%Y-%m-%d')
        df['OriginalLastDayOfCobra'] = pd.to_datetime(df['OriginalLastDayOfCobra'], format='%Y-%m-%d')
        return df


    @st.cache
    def convert_df(df):
        return df.to_csv().encode('utf-8')

    # Dependent And Dependent Plan Information
    dependent_df = df.iloc[indexes[4] - 1:]
    dependent_df = new_header(dependent_df)
    dependent_df.columns = dependent_df.columns.fillna('to_drop')
    dependent_df.drop('to_drop', axis=1, inplace=True)
    dependent_df = dependent_df.astype(str)

    # -----Sidebar filter Member Information-----
    st.sidebar.header('Please filter here:')

    st.sidebar.header('Member Information')
    Program = st.sidebar.multiselect('Select Benefit Program', options=final_df.ClientDivisionName.unique())
    sp_info = st.sidebar.multiselect('Select Coverage Level', options=final_df.CoverageLevelTypeDesc.unique())
    desc = st.sidebar.multiselect('Select Plan Status:', options=final_df.StatusDesc.unique())
    carrier = st.sidebar.multiselect('Select Carrier:', options=final_df.CarrierName.unique())
    insurance_type = st.sidebar.multiselect('Select Insurance Type:', options=final_df.InsuranceTypeDesc.unique())
    relationship = st.sidebar.multiselect('Select Relationship:', options=dependent_df.Relationship.unique())


    final_df = pandas_datatime(final_df)

    # -----Sidebar Number of Days slider-----
    st.sidebar.header('Filter By Member Age')
    days_slider = st.sidebar.slider('Number of Days', -120, 120, 0)
    days_slider = int(days_slider)

    days_60 = date.today()
    days_60_n = days_60 - timedelta(days=days_slider)
    days_60_p = days_60 + timedelta(days=days_slider)

    # filter by end of continuation through days slider
    end_of_cont_df = final_df[final_df['OriginalLastDayOfCobra'] == days_slider]

    # check if days slider is 0
    if days_slider == 0 or days_slider == 0.0:
        st.sidebar.write('Today date: {}'. format(days_60))

    elif days_slider > 0 and days_slider < 120:
        st.sidebar.write('+120 days: {}'. format(days_60_p))

    elif days_slider < 0 and days_slider > -120:
        st.sidebar.write('-120 days: {}'. format(days_60_n))


    final_df['Age'] = final_df['DOB'].apply(check_age)

    # -----Sidebar Age filter-----
    age_slider = st.sidebar.slider('Age', 0, 100, 0)
    age_slider = int(age_slider)

    # check if age slider is 0
    if age_slider == 0 or age_slider == 0.0:
        st.sidebar.write('Age: {}'. format(age_slider))

    elif age_slider > 0 and age_slider < 100:
        st.sidebar.write('Age: {}'. format(age_slider))

    # filter age based on the slider
    age_df = final_df[final_df['Age'] == age_slider]

    # function to filter by multiselect options and days slider and age slider
    def filter_df(df, Program, sp_info, desc, carrier, insurance_type, age_slider):
        if Program:
            df = df[df['ClientDivisionName'].isin(Program)]
        if sp_info:
            df = df[df['CoverageLevelTypeDesc'].isin(sp_info)]
        if desc:
            df = df[df['StatusDesc'].isin(desc)]
        if carrier:
            df = df[df['CarrierName'].isin(carrier)]
        if insurance_type:
            df = df[df['InsuranceTypeDesc'].isin(insurance_type)]
        if age_slider:
            df = df[df['Age'] == age_slider]
        return df

    # unique member id
    final_df = final_df.drop_duplicates(subset='MemberID')

    final_df = filter_df(final_df, Program, sp_info, desc, carrier, insurance_type, age_slider)

    st.markdown('### Member Information')
    st.write(final_df)

    #st.subheader("End of Continuation")
    #st.write(final_df[final_df['OriginalLastDayOfCobra'] == days_slider])

    final_csv = convert_df(final_df)
    st.download_button("Download Member Information", final_csv, "Member.csv", "text/csv", key='download-csv')

    # ----Dependent Information----

    # Age in dependent_df
    dependent_df['Age'] = dependent_df['DOB'].apply(check_age)
    st.sidebar.subheader('Filter By Dependent Record')

    # -----Sidebar Age filter-----
    dep_age_slider = st.sidebar.slider('Dependent Age', 0, 100, 0)
    dep_age_slider = int(dep_age_slider)

    # check if age slider is 0
    if dep_age_slider == 0 or dep_age_slider == 0.0:
        st.sidebar.write('Age: {}'. format(dep_age_slider))

    elif dep_age_slider > 0 and dep_age_slider < 100:
        st.sidebar.write('Age: {}'. format(dep_age_slider))

    # filter age based on the slider
    dependent_df = dependent_df[dependent_df['Age'] == dep_age_slider]

    def filter_dependent(df, relationship, dep_age_slider):
        if relationship:
            df = df[df['Relationship'].isin(relationship)]
        if dep_age_slider:
            df = df[df['Age'] == dep_age_slider]
        return df

    dependent_df = filter_dependent(dependent_df, relationship, dep_age_slider)

    # filter same member id in dependent df
    dependent_df = dependent_df[dependent_df['MemberID'].isin(final_df['MemberID'])]

    st.markdown('### Dependent Information')
    st.write(dependent_df)
    dependent_csv = convert_df(dependent_df)
    st.download_button("Download Dependent Information", dependent_csv, "Dependent.csv", "text/csv", key='download-csv')

    # -----End of COBRA----
    st.sidebar.header('End of Continuation')





hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)


