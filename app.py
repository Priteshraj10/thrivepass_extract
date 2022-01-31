import streamlit as st
import pandas as pd
from PIL import Image
from datetime import datetime, date, timedelta
import base64
import json
import pickle
import uuid
import re
import io

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
    plan = st.sidebar.multiselect('Select Plan Type:', options=final_df.PlanName.unique())
    desc = st.sidebar.multiselect('Select Plan Description:', options=final_df.StatusDesc.unique())
    carrier = st.sidebar.multiselect('Select Carrier:', options=final_df.CarrierName.unique())

    # function pandas datatime
    def pandas_datatime(df):
        df['DOB'] = pd.to_datetime(df['DOB'], format='%Y-%m-%d')
        return df

    final_df = pandas_datatime(final_df)

    # -----Sidebar Age Range slider-----
    st.sidebar.header('Age Range')
    age_range = st.sidebar.slider('Age Range', 0, 100, (0, 100))

    # -----Sidebar Number of Days slider-----
    st.sidebar.header('Number of Days')
    days = st.sidebar.slider('Number of Days', 0, 100, (0, 100))

    """

    # Age conversion to years from DOB
    def dep_age(date):
        born = datetime.strptime(str(date), "%Y-%m-%d %H:%M:%S").date()
        today = date.today()
        sixty_days = today + timedelta(days=days)
        return sixty_days.year - born.year - ((sixty_days.month, today.day) < (born.month, born.day))

    final_df['Age'] = final_df['DOB'].apply(dep_age)
    """

    final_df = final_df.query(
        f"ClientDivisionName == @Program" or "CoverageLevelTypeDesc == @sp_info" or "StatusDesc == @desc" or "CarrierName == @carrier" or
        "PlanName == @plan" or "Age >= @age_range" or "Days >= @days")
    st.write(final_df)

    """
    # -----Sidebar filter Plan Information-----
    st.sidebar.header('Dependent information')
    Plan_name = st.sidebar.multiselect('Select Plan Name:', options=dependent_df.PlanName.unique())
    insur_type = st.sidebar.multiselect('Select Insurance Type:', options=dependent_df.InsuranceTypeName.unique())
    state = st.sidebar.multiselect('Select State:', options=dependent_df.StateOrProvince.unique())
    Country = st.sidebar.multiselect('Select County:', options=dependent_df.Country.unique())
    dependent_df = dependent_df.query(f"PlanName == @Plan_name" or "InsuranceTypeName == @insur_type" or "StateOrProvince == @state" or "Country == @Country")
    st.sidebar.header('Dependent Information')
    st.write(dependent_df)
    """

"""
  no_days = st.sidebar.radio(label='Radio buttons', options=['60 days before', '60 days after'])

  if no_days == '60 days before':
      final_df['DOB'] = final_df['DOB'].apply(lambda x: x - timedelta(days=60))
  elif no_days == '60 days after':
      final_df['DOB'] = final_df['DOB' \
                                 ''].apply(lambda x: x + timedelta(days=60))

      
  days_before = (date.today()-timedelta(days=60)).isoformat()
  days_after = (date.today()+timedelta(days=60)).isoformat()
  
  # Age_data = final_df[final_df['Age'] > a.year]

  final_df = final_df.query(f"ClientDivisionName == @Program" and "CoverageLevelTypeDesc == @sp_info" and "StatusDesc == @desc")

  # ---- MAIN PAGE ----
  st.header("Ecolab")
  st.write(final_df)

"""

def age(born):
    born = datetime.strptime(str(born), "%Y-%m-%d %H-%m-%s").date()
    today = date.today()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))


# 65th birthday
def addYears(d, years):
    year=d.year+years
    return year


def download_button(object_to_download, download_filename, button_text, pickle_it=False):
    if pickle_it:
        try:
            object_to_download = pickle.dumps(object_to_download)
        except pickle.PicklingError as e:
            st.write(e)
            return None

    else:
        if isinstance(object_to_download, bytes):
            pass

        elif isinstance(object_to_download, pd.DataFrame):
            #object_to_download = object_to_download.to_csv(index=False)
            towrite = io.BytesIO()
            object_to_download = object_to_download.to_excel(towrite, encoding='utf-8', index=False, header=True)
            towrite.seek(0)

        # Try JSON encode for everything else
        else:
            object_to_download = json.dumps(object_to_download)

    try:
        # some strings <-> bytes conversions necessary here
        b64 = base64.b64encode(object_to_download.encode()).decode()

    except AttributeError as e:
        b64 = base64.b64encode(towrite.read()).decode()

    button_uuid = str(uuid.uuid4()).replace('-', '')
    button_id = re.sub('\d+', '', button_uuid)

    custom_css = f""" 
        <style>
            #{button_id} {{
                display: inline-flex;
                align-items: center;
                justify-content: center;
                background-color: rgb(255, 255, 255);
                color: rgb(38, 39, 48);
                padding: .25rem .75rem;
                position: relative;
                text-decoration: none;
                border-radius: 4px;
                border-width: 1px;
                border-style: solid;
                border-color: rgb(230, 234, 241);
                border-image: initial;
            }} 
            #{button_id}:hover {{
                border-color: rgb(246, 51, 102);
                color: rgb(246, 51, 102);
            }}
            #{button_id}:active {{
                box-shadow: none;
                background-color: rgb(246, 51, 102);
                color: white;
                }}
        </style> """

    dl_link = custom_css + f'<a download="{download_filename}" id="{button_id}" href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}">{button_text}</a><br></br>'

    return dl_link

hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)
