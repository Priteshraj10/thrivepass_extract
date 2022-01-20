import streamlit as st
import pandas as pd
from PIL import Image
from datetime import datetime, date, timedelta
import base64
import json
import pickle
import uuid
import re
import os
import codecs
import io
from matplotlib import pyplot as plt
import plotly.graph_objects as go

image = Image.open('assets/tp logo day.png')
st.set_page_config(page_title='Ecolab COBRA',
                   page_icon=image, layout='wide')
st.image('assets/tp-wordmark-day.png', width=400)

uploaded_file = st.file_uploader("Choose a file")
if uploaded_file is not None:
    df = pd.read_excel(uploaded_file, skiprows=1)

    # str contains method
    mask = df[df['MemberID'].str.contains(r"MemberID", na=False)]

    # indexes of mask
    indexes = mask.index.values

    # member information dataframe
    inital_val = 0
    member_df = df.loc[0:indexes[0] - 3]
    st.subheader('Member Information')
    st.write(member_df)

    plan_df = df.iloc[indexes[0]:indexes[1] - 2]
    st.subheader('Plan Information')
    st.write(plan_df)
    final_df = pd.merge(plan_df, member_df, on='MemberID', suffixes=('', '_delme'))
    final_df = final_df[[c for c in final_df.columns if not c.endswith('_delme')]]



    dependent_df = df.iloc[indexes[4]:]
    st.subheader('Dependent Information')
    st.write(dependent_df)

    # -----Sidebar filter Member Information-----
    st.sidebar.subheader('Please filter here')
    if st.sidebar.checkbox('Member Information'):
        Program = st.sidebar.multiselect('Select Benefit Program', options=final_df.ClientDivisionName.unique())
        sp_info = st.sidebar.multiselect('Select Coverage Level', options=final_df.CoverageLevelTypeDesc.unique())
        plan = st.sidebar.multiselect('Select Plan Type:', options=final_df.PlanName.unique())
        desc = st.sidebar.multiselect('Select Plan Description:', options=final_df.StatusDesc.unique())
        carrier = st.sidebar.multiselect('Select Carrier:', options=final_df.CarrierName.unique())
        final_df = final_df.query(
            f"ClientDivisionName == @Program" and "CoverageLevelTypeDesc == @sp_info" and "StatusDesc == @desc" and "CarrierName == @carrier" and "PlanName == @plan")
        st.subheader('Member information and Plan information')
        st.write(final_df)

    elif st.sidebar.checkbox('Dependent Information'):
        st.write(dependent_df)


"""
  # ---- SIDEBAR ----
  st.sidebar.header("Please Filter Here:")

  Program = st.sidebar.multiselect(
      "Select the Benefit program:",
      options=final_df["ClientDivisionName"].unique()
  )

  sp_info = st.sidebar.multiselect(
      "Select the Coverage Level:",
      options=final_df["ClientDivisionID"].unique()
  )


  desc = st.sidebar.multiselect(
      "Select the Status:",
      options=final_df["StatusDesc"].unique()
  )

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



def age(born):
    born = datetime.strptime(str(born), "%Y-%m-%d %H-%m-%s").date()
    today = date.today()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))


# 65th birthday
def addYears(d, years):
    year=d.year+years
    return year
"""

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
