import os
import pandas as pd
import gspread as gs
from google.oauth2.service_account import Credentials
from google import genai
from dotenv import load_dotenv
import streamlit as st

# configuration
SHEET_NAME = "Client Monthly Check-In (Responses)"
GEMINI_MODEL = "gemini-3.1-flash-lite-preview"

# -- connect to Google sheets

# define the scope
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# credentials from JSON file
creds = Credentials.from_service_account_file("credentials.json", scopes=scope)

# authorize

client = gs.authorize(creds)

# open spreadsheet
sheet = client.open(SHEET_NAME).sheet1

# -- connect to Gemini

# load API key
load_dotenv()
gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# -- parse AI response

# parse Gemini's structured response into individual fields
def parse_analysis(text):
    lines = text.strip().split('\n')
    parsed = {}
    for line in lines:
        if line.startswith('SUMMARY:'):
            parsed['Summary'] = line.replace('SUMMARY:', '').strip()
        elif line.startswith('URGENCY:'):
            parsed['Urgency'] = line.replace('URGENCY:', '').strip()
        elif line.startswith('CATEGORY:'):
            parsed['Category'] = line.replace('CATEGORY:', '').strip()
        elif line.startswith('ACTION:'):
            parsed['Action'] = line.replace('ACTION:', '').strip()
    return parsed

# -- load and analyze data
@st.cache_data(ttl=300)
def load_data():
    
    # pull all data to a dataframe
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
    
    # map spreadsheet columns as simpler column names
    df.columns = ['Timestamp', 'First Name', 'Last Name', 'Phone',
                  'Situation Type', 'Details', 'Connect', 'Contact', 'Email']
    
    # set client name as first and last name
    df['Client Name'] = df['First Name'] + ' ' + df['Last Name']
    
    # only analyze rows where client provided details
    df_with_details = df[df['Details'].str.strip() != ''].copy()

    # empty list to store each analyzed row
    parsed_rows = []

    # loop through each client response that has details
    for index, row in df_with_details.iterrows():
        
        # extract relevant fields from the row
        client_name = row['Client Name']
        situation = row['Situation Type']
        details = row['Details']

        # build the prompt with client context and strict formatting instructions
        prompt = f"""You are an assistant helping relationship managers at a concierge community bank.

A client named {client_name} submitted the following monthly check-in update:
Situation type they selected: {situation}
Their description: "{details}"

Please respond in exactly this format with no extra text:
SUMMARY: [one sentence summary]
URGENCY: [Low, Medium, or High]
CATEGORY: [Legal, Business Change, Major Purchase, Personal Life Event, Financial Change, or General Update]
ACTION: [recommended action for the banker]"""

        # send the prompt to Gemini and get a response
        response = gemini_client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt
        )

        # parse Gemini's response into structured fields
        parsed = parse_analysis(response.text)

        # append the full row with AI analysis to the results list
        parsed_rows.append({
            'Name': client_name,
            'Timestamp': row['Timestamp'],
            'Phone': row['Phone'],
            'Email': row['Email'],
            'Situation Type': situation,
            'Details': details,
            'Connect': row['Connect'],
            'Contact': row['Contact'],
            'Summary': parsed.get('Summary', ''),
            'Urgency': parsed.get('Urgency', ''),
            'Category': parsed.get('Category', ''),
            'Recommended Action': parsed.get('Action', '')
        })

    # convert results list into a final dataframe
    return pd.DataFrame(parsed_rows)

# -- Streamlit dashboard
st.title("Client Check-In Dashboard")
st.markdown("AI-powered client monitoring for relationship managers")

with st.spinner("Loading client responses..."):
    df_final = load_data()

if df_final.empty:
    st.info("No client responses with details found yet.")
else:
    
    # summary metrics at the top
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Responses", len(df_final))
    col2.metric("High Urgency", len(df_final[df_final['Urgency'] == 'High']))
    col3.metric("Wants to Connect", len(df_final[df_final['Connect'] == 'Yes, I\'d love to connect']))

    st.divider()

    # urgency filter
    urgency_filter = st.selectbox("Filter by Urgency", ["All", "High", "Medium", "Low"])
    if urgency_filter != "All":
        df_display = df_final[df_final['Urgency'] == urgency_filter]
    else:
        df_display = df_final

    # display table
    st.dataframe(
        df_display[['Timestamp', 'Name', 'Urgency', 'Category', 'Summary', 'Recommended Action', 'Connect', 'Contact']],
        use_container_width=True
    )

    st.divider()

    # client detail view
    st.subheader("Client Detail View")
    selected_client = st.selectbox("Select a client to view full details", df_display['Name'].tolist())

    if selected_client:
        client_row = df_display[df_display['Name'] == selected_client].iloc[0]
        st.write(f"**Submitted:** {client_row['Timestamp']}")
        st.write(f"**Phone:** {client_row['Phone']}")
        st.write(f"**Email:** {client_row['Email']}")
        st.write(f"**Urgency:** {client_row['Urgency']}")
        st.write(f"**Category:** {client_row['Category']}")
        st.write(f"**What they said:** {client_row['Details']}")
        st.write(f"**AI Summary:** {client_row['Summary']}")
        st.write(f"**Recommended Action:** {client_row['Recommended Action']}")
        st.write(f"**Wants to connect:** {client_row['Connect']}")
        st.write(f"**Preferred contact method:** {client_row['Contact']}")