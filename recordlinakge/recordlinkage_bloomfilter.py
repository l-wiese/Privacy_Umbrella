import pandas as pd
import streamlit as st
from bitarray import bitarray
import mmh3
from metaphone import doublemetaphone
import re
import dateparser
import Levenshtein

# Define a simple Bloom filter class
class BloomFilter:
    def __init__(self, size, hash_count):
        self.size = size
        self.hash_count = hash_count
        self.bit_array = bitarray(size)
        self.bit_array.setall(0)

    def add(self, item):
        processed_item = preprocess_text(item)
        for i in range(self.hash_count):
            digest = mmh3.hash(processed_item, i) % self.size
            self.bit_array[digest] = 1

    def lookup(self, item):
        processed_item = preprocess_text(item)
        for i in range(self.hash_count):
            digest = mmh3.hash(processed_item, i) % self.size
            if self.bit_array[digest] == 0:
                return False
        return True

# Helper functions for standardization and phonetic encoding
def preprocess_text(text):
    text = text.lower().strip()
    text = re.sub(r'\s+', ' ', text)
    return text

def standardize_address(address):
    address = preprocess_text(address)
    # Normalize common abbreviations
    address = re.sub(r'\bstr\b\.?', 'straße', address)
    # Normalize address ranges, consider only the first number in a range
    address = re.sub(r'\b(\d+)\s*-\s*\d+', r'\1', address)
    # Add more patterns as needed based on your dataset
    return address

def standardize_date(date_str):
    date_obj = dateparser.parse(date_str)
    if date_obj:
        return date_obj.strftime('%d-%m-%Y')
    return date_str

def phonetic_encoding(name):
    primary, _ = doublemetaphone(name)
    return primary

def is_similar_name(name1, name2):
    return Levenshtein.ratio(name1, name2) > 0.8  # Threshold can be adjusted

def is_similar_address(address1, address2):
    return Levenshtein.ratio(address1, address2) > 0.8  # Threshold can be adjusted

def create_bloom_filter(record, bloom_filter):
    for element in record:
        element = preprocess_text(element)
        bloom_filter.add(element)

# Streamlit app setup
st.title('Privacy-Preserving Record Linkage (PPRL)')

# File uploader widgets
file1 = st.file_uploader("Upload first dataset", type=['csv'])
file2 = st.file_uploader("Upload second dataset", type=['csv'])

if file1 and file2:
    df1 = pd.read_csv(file1)
    df2 = pd.read_csv(file2)

    # Display a preview of the two datasets
    st.write("Dataset 1 Preview:")
    st.write(df1)

    st.write("Dataset 2 Preview:")
    st.write(df2)

    bloom_filter1 = BloomFilter(size=10000, hash_count=10)
    bloom_filter2 = BloomFilter(size=10000, hash_count=10)

    for _, row in df1.iterrows():
        encoded_name = phonetic_encoding(row['Name'])
        standardized_dob = standardize_date(row['DOB'])
        standardized_address = standardize_address(row['Address'])
        print(f"DF1 Address: {row['Address']} -> {standardized_address}")  # Debug print
        create_bloom_filter([encoded_name, standardized_dob, standardized_address], bloom_filter1)

    for _, row in df2.iterrows():
        encoded_name = phonetic_encoding(row['Name'])
        standardized_dob = standardize_date(row['DOB'])
        standardized_address = standardize_address(row['Address'])
        print(f"DF2 Address: {row['Address']} -> {standardized_address}")  # Debug print
        create_bloom_filter([encoded_name, standardized_dob, standardized_address], bloom_filter2)

    # Compare Bloom filters to find potential matches
    potential_matches = []
    for _, row in df1.iterrows():
        standardized_dob = standardize_date(row['DOB'])
        standardized_address = standardize_address(row['Address'])
        for _, row2 in df2.iterrows():
            if standardized_dob == standardize_date(row2['DOB']) and \
                    is_similar_address(standardized_address, standardize_address(row2['Address'])):
                potential_matches.append(row['Name'])
                break  # Assuming one-to-one match

    st.write("Potential Matches Found:")
    st.write(potential_matches)
