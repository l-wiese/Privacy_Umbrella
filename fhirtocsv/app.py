import streamlit as st
import pandas as pd
import os
import io
from io import StringIO, BytesIO
import streamlit as st
import pandas as pd
import json
from typing import Any, Dict
from io import StringIO
import base64
# Function to flatten JSON
def flatten_dict(d, parent_key='', sep='_'):
    items = []
    if isinstance(d, dict):
        for k, v in d.items():
            new_key = f'{parent_key}{sep}{k}' if parent_key else k
            if isinstance(v, dict):
                items.extend(flatten_dict(v, new_key, sep=sep).items())
            elif isinstance(v, list):
                for i, item in enumerate(v):
                    if isinstance(item, dict):
                        items.extend(flatten_dict(item, f'{new_key}{sep}{i}', sep=sep).items())
                    else:
                        items.append((f'{new_key}{sep}{i}', item))
            else:
                items.append((new_key, v))
    elif isinstance(d, list):
        for i, item in enumerate(d):
            items.extend(flatten_dict(item, f'{parent_key}{sep}{i}', sep=sep).items())
    else:
        items.append((parent_key, d))
    return dict(items)


# Function to parse FHIR JSON and return a DataFrame
def parse_fhir(json_data):
    all_data = []
    for entry in json_data['entry']:
        flattened_data = flatten_dict(entry)
        all_data.append(flattened_data)
    return pd.DataFrame(all_data)

# Function to extract observation data from a DataFrame
def extract_labrotory_data(df):
    observation_data = set()
    if 'resource_resourceType' in df and 'resource_code_text' in df:
        observation_rows = df[df['resource_resourceType'] == 'Observation']
        for _, row in observation_rows.iterrows():
            code = row['resource_code_coding_0_code']
            code_text = row['resource_code_text']
            value_code = row['resource_valueQuantity_code']
            observation_data.add((code, code_text, value_code))
    return observation_data
def extract_medication_data(df):
    observation_data = set()
    if 'resource_resourceType' in df and 'resource_code_text' in df:
        observation_rows = df[df['resource_resourceType'] == 'Medication']
        for _, row in observation_rows.iterrows():
            code = row.get('resource_code_coding_0_code', '')
            code_text = row.get('resource_code_text', '')
            observation_data.add((code, code_text))
    return observation_data

def extract_condition_data(df):
    observation_data = set()
    if 'resource_resourceType' in df and 'resource_code_text' in df:
        observation_rows = df[df['resource_resourceType'] == 'Condition']
        # Iterate through observation rows to collect unique pairs
        for _, row in observation_rows.iterrows():
            code = row['resource_code_coding_0_code']
            code_text = row['resource_code_text']
            observation_data.add((code, code_text))
    return observation_data
def extract_procedure_data(df):
    observation_data = set()
    if 'resource_resourceType' in df and 'resource_code_text' in df:
        observation_rows = df[df['resource_resourceType'] == 'Procedure']
        # Iterate through observation rows to collect unique pairs
        for _, row in observation_rows.iterrows():
            code = row['resource_code_coding_0_code']
            code_text = row['resource_code_text']
            observation_data.add((code, code_text))
    return observation_data


# The rest of your Streamlit app code where you call cross_reference_files
# ...

# Function to cross-reference patient files with other datasets
def cross_reference_files(patient_files, medication_files):
    # Create a list to store summary data for all patients
    summary_data = []

    # Load all medication codes from medication files into a set for fast lookup
    medication_codes = set()
    for med_file in medication_files:
        med_df = pd.read_csv(med_file, dtype={'Code': str})  # Ensure correct column name 'Code' is used
        medication_codes.update(med_df['Code'].dropna().unique())  # Use 'Code' column to update the set

    # Iterate through each patient file
    for patient_file in patient_files:
        patient_df = pd.read_csv(patient_file)
        # Extract patient ID from the first row of the 'resource_id' column
        patient_id = patient_df['resource_id'].iloc[0]
        patient_gender = patient_df['resource_gender'].iloc[0]
        patient_birthDate= patient_df['resource_birthDate'].iloc[0]
        patient_family = patient_df['resource_name_0_family'].iloc[0]
        patient_name= patient_df['resource_name_0_given_0'].iloc[0]
        patient_address= patient_df['resource_address_0_line_0'].iloc[0]
        patient_city = patient_df['resource_address_0_city'].iloc[0]
        patient_postalCode = patient_df['resource_address_0_postalCode'].iloc[0]
        patient_country= patient_df['resource_address_0_country'].iloc[0]
        patient_insurance=patient_df['resource_generalPractitioner_0_display'].iloc[0]
        # Create a summary row for each patient
        summary_row = {'patient_id': patient_id, 'patient_gender':patient_gender,'patient_birthDate':patient_birthDate,
                       'patient_family':patient_family,'patient_name':patient_name,'patient_address':patient_address,
                       'patient_city':patient_city,'patient_postalCode':patient_postalCode,
                       'patient_country':patient_country,'patient_insurance':patient_insurance}
        observation_data_medication = set()
        if 'resource_resourceType' in patient_df.columns and 'resource_code_coding_0_code' in patient_df.columns:
            observation_rows = patient_df[patient_df['resource_resourceType'] == 'Medication']
            for _, row in observation_rows.iterrows():
                code = row.get('resource_code_coding_0_code', '')
                observation_data_medication.add(code)

        # Check if each medication code in the patient file is in the medication file
        for med_code in medication_codes:
            # The column for the summary should probably be something like 'medication_{med_code}'
            summary_row[med_code] = 1 if med_code in observation_data_medication else 0

        # Append the summary row to the summary data list
        summary_data.append(summary_row)

    # Convert summary data to DataFrame and return
    return pd.DataFrame(summary_data)


# Function to convert a DataFrame to a downloadable Excel file
def to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Sheet1', index=False)
        writer.save()
    processed_data = output.getvalue()
    return processed_data

# Streamlit app layout
st.title('Healthcare Data Processor')

# Sidebar for navigation
tool = st.sidebar.selectbox(
    'Choose a tool',
    ('FHIR to CSV Converter', 'Medication Data Extractor', 'Laboratory Studies Data Extractor',
     'Conditions Data Extractor', 'Procedure Data Extractor', 'Patient Data Cross-Referencer')
)

if tool == 'FHIR to CSV Converter':
    # FHIR to CSV Converter logic
    st.markdown("## Upload FHIR File")
    uploaded_file = st.file_uploader("Choose a FHIR JSON file", type="json")
    if uploaded_file:
        json_data = pd.read_json(uploaded_file)
        df = parse_fhir(json_data)
        st.dataframe(df)
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("Download as CSV", csv, "file.csv", "text/csv", key='download-csv')

elif tool == 'Medication Data Extractor':
    # Medication Data Extractor logic
    st.markdown("## Upload CSV Files for Medication Data")
    uploaded_files = st.file_uploader("Choose CSV files", accept_multiple_files=True, type="csv", key="medication_data_uploader")
    all_medication_data = pd.DataFrame()

    if uploaded_files:
        for uploaded_file in uploaded_files:
            df = pd.read_csv(uploaded_file)
            medication_data = extract_medication_data(df)
            all_medication_data = pd.concat([all_medication_data, pd.DataFrame(medication_data, columns=['Code', 'Description'])], ignore_index=True)

        if not all_medication_data.empty:
            # Remove duplicates and preview the data
            unique_medication_data = all_medication_data.drop_duplicates(subset=['Code'])
            st.markdown("### Extracted Medication Data:")
            st.dataframe(unique_medication_data)

            # Provide option to download as CSV
            csv = unique_medication_data.to_csv(index=False).encode('utf-8')
            st.download_button(label="Download Compiled Medication Data as CSV",
                                data=csv,
                                file_name='medication_data.csv',
                                mime='text/csv')

elif tool == 'Laboratory Studies Data Extractor':
    # Laboratory Studies Data Extractor logic
    st.markdown("## Upload CSV Files for Laboratory Data")
    uploaded_files = st.file_uploader("Choose CSV files", accept_multiple_files=True, type="csv", key="lab_data_uploader")
    all_lab_data = pd.DataFrame()

    if uploaded_files:
        for uploaded_file in uploaded_files:
            df = pd.read_csv(uploaded_file)
            lab_data = extract_labrotory_data(df)
            all_lab_data = pd.concat([all_lab_data, pd.DataFrame(lab_data, columns=["code","type","Value Quantity"])], ignore_index=True)

        if not all_lab_data.empty:
            # Remove duplicates and preview the data
            unique_lab_data = all_lab_data.drop_duplicates(subset=['type'])
            st.markdown("### Extracted Laboratory Data:")
            st.dataframe(unique_lab_data)

            # Provide option to download as CSV
            csv = unique_lab_data.to_csv(index=False).encode('utf-8')
            st.download_button(label="Download Compiled Laboratory Data as CSV",
                                data=csv,
                                file_name='lab_data.csv',
                                mime='text/csv')

elif tool == 'Conditions Data Extractor':
    # Conditions Data Extractor logic
    st.markdown("## Upload CSV Files for Conditions Data")
    uploaded_files = st.file_uploader("Choose CSV files", accept_multiple_files=True, type="csv", key="conditions_data_uploader")
    all_condition_data = pd.DataFrame()

    if uploaded_files:
        for uploaded_file in uploaded_files:
            df = pd.read_csv(uploaded_file)
            condition_data = extract_condition_data(df)
            all_condition_data = pd.concat([all_condition_data, pd.DataFrame(condition_data, columns=["code","type"])], ignore_index=True)

        if not all_condition_data.empty:
            # Remove duplicates and preview the data
            unique_condition_data = all_condition_data.drop_duplicates(subset=['code'])
            st.markdown("### Extracted Conditions Data:")
            st.dataframe(unique_condition_data)

            # Provide option to download as CSV
            csv = unique_condition_data.to_csv(index=False).encode('utf-8')
            st.download_button(label="Download Compiled Conditions Data as CSV",
                                data=csv,
                                file_name='conditions_data.csv',
                                mime='text/csv')

elif tool == 'Procedure Extractor':
    # Procedure Extractor logic
    st.markdown("## Upload CSV Files for Procedure Data")
    uploaded_files = st.file_uploader("Choose CSV files", accept_multiple_files=True, type="csv", key="procedure_data_uploader")
    all_procedure_data = pd.DataFrame()

    if uploaded_files:
        for uploaded_file in uploaded_files:
            df = pd.read_csv(uploaded_file)
            procedure_data = extract_procedure_data(df)
            all_procedure_data = pd.concat([all_procedure_data, pd.DataFrame(procedure_data, columns=["code","type"])], ignore_index=True)

        if not all_procedure_data.empty:
            # Remove duplicates and preview the data
            unique_procedure_data = all_procedure_data.drop_duplicates(subset=['code'])
            st.markdown("### Extracted Procedure Data:")
            st.dataframe(unique_procedure_data)

            # Provide option to download as CSV
            csv = unique_procedure_data.to_csv(index=False).encode('utf-8')
            st.download_button(label="Download Compiled Procedure Data as CSV",
                                data=csv,
                                file_name='procedure_data.csv',
                                mime='text/csv')
# New tool for cross-referencing patient data
elif tool == 'Patient Data Cross-Referencer':
    st.markdown("## Upload Patient Files")
    uploaded_patient_files = st.file_uploader("Choose Patient CSV files", accept_multiple_files=True, type="csv", key="patient_files_uploader")

    st.markdown("## Upload Medication Files")
    uploaded_medication_files = st.file_uploader("Choose Medication CSV files", accept_multiple_files=True, type="csv", key="medication_files_uploader")

    # st.markdown("## Upload Laboratory Studies Files")
    #  uploaded_procedure_files = st.file_uploader("Choose Procedure CSV files", accept_multiple_files=True, type="csv", key="lab_files_uploader")

    #  st.markdown("## Upload Conditions Files")
    #  uploaded_procedure_files = st.file_uploader("Choose Procedure CSV files", accept_multiple_files=True, type="csv",
    #        key="conditions_files_uploader")

    #   st.markdown("## Upload Procedure Files")
    #   uploaded_procedure_files = st.file_uploader("Choose Procedure CSV files", accept_multiple_files=True, type="csv",
    #                        key="procedure_files_uploader")


    if st.button("Cross-Reference Data"):
        if uploaded_patient_files and uploaded_medication_files:
            summary_df = cross_reference_files(uploaded_patient_files, uploaded_medication_files)
            st.dataframe(summary_df)

            # Convert DataFrame to CSV for download
            csv = summary_df.to_csv(index=False).encode('utf-8')
            st.download_button("Download Cross-Referenced Data", csv, "cross_referenced_data.csv", "text/csv", key='download-cross-referenced-data')
        else:
            st.error("Please upload patient, medication, and procedure files.")


def get_image_base64(path):
    with open(path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# Path to your image
image_path_item = 'C:\\Users\\ayabe\\OneDrive\\Desktop\\FraunhoferITEM\\Fraunhofer_ITEM_Logo.jpg'
image_path_mainz = 'C:\\Users\\ayabe\\OneDrive\\Desktop\\FraunhoferITEM\\Mainz.png'
image_path_goethe='C:\\Users\\ayabe\\OneDrive\\Desktop\\FraunhoferITEM\\Goethe_University_logo.jpg'
# Convert the image to base64
encoded_image_item = get_image_base64(image_path_item)
encoded_image_mainz = get_image_base64(image_path_mainz)
encoded_image_goethe = get_image_base64(image_path_goethe)

# Function to add multiple images to the footer
def add_footer(encoded_image_item, encoded_image_mainz, encoded_image_goethe):
    st.markdown(
        f"""
        <style>
        .footer {{
            position: fixed;
            bottom: 0;
            left: 0;
            width: 100%;
            background-color: white;
            text-align: center;
            padding: 10px;
        }}
        </style>
        <div class='footer'>
            <img src='data:image/jpg;base64,{encoded_image_item}' width='120'>
            <img src='data:image/png;base64,{encoded_image_mainz}' width='120'>
            <img src='data:image/jpg;base64,{encoded_image_goethe}' width='120'>
        </div>
        """,
        unsafe_allow_html=True
    )

# Call the function with the three images
add_footer(encoded_image_item, encoded_image_mainz, encoded_image_goethe)
