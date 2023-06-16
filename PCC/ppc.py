# -*- coding: utf-8 -*-
"""
@author: ahoiemma
"""


from scipy.stats import pearsonr
import pandas as pd
import os


def calculate(file, is_original, quasi_identifier_x, is_x_range, quasi_identifier_y, is_y_range):
    # Load Dataset
    if is_original == True:
        filepath = os.path.join('../original_datasets/', file)
        df = pd.read_csv(filepath)
    else:
        filepath = os.path.join('../anonymized_datasets/', file)
        df = pd.read_csv(filepath)

    # Define quasi identifiers
    if is_x_range == True:
        x = pd.Categorical(df[quasi_identifier_x]).codes
    else:
        x = df[quasi_identifier_x].squeeze()

    if is_y_range == True:
        y = pd.Categorical(df[quasi_identifier_y]).codes
    else:
        y = df[quasi_identifier_y].squeeze()

    # Calculate Pearson Corellation Coefficiant and P-Value
    pcc, pvalue = pearsonr(x, y)
    print(f"PCC: {pcc}")
    print(f"P-Value: {pvalue}\n")


def calculate_heart():
    # Original Data
    print("\nOriginal Heart Data:")
    calculate('heart.csv', True, 'age', False, 'sex', False)

    # V1 Data
    print("V1 Heart Data:")
    calculate('v1_heart.csv', False, 'age_range', True, 'sex', False)

    # V2 Data
    print("V2 Heart Data:")
    calculate('v2_heart.csv', False, 'age', True, 'sex', False)

    # V3 Data
    print("V3 Heart Data:")
    calculate('v3_heart.csv', False, 'age_range', True, 'sex', False)

    # V4 Data
    print("V4 Heart Data:")
    calculate('v4_heart.csv', False, 'age_range', True, 'sex', False)

    # V5 Data
    print("V5 Heart Data:")
    calculate('v5_heart.csv', False, 'age', False, 'sex', False)


def calculate_sepsis():
    # Original Data
    print("\nOriginal Sepsis Data:")
    calculate('sepsis.csv', True, 'Age', False, 'Gender', False)

    # V1 Data
    print("V1 Sepsis Data:")
    calculate('v1_sepsis.csv', False, 'Age', True, 'Gender', False)

    # V2 Data
    print("V2 Sepsis Data:")
    calculate('v2_sepsis.csv', False, 'Age', True, 'Gender', False)

    # V3 Data
    print("V3 Sepsis Data:")
    calculate('v3_sepsis.csv', False, 'Age', False, 'Gender', False)

    # V4 Data
    print("V4 Sepsis Data:")
    calculate('v4_sepsis.csv', False, 'Age', False, 'Gender', False)


def main():
    selection = input("Press 1 for Heart, Press 2 for Sepsis\n")
    if selection == "1":
        calculate_heart()
    elif selection == "2":
        calculate_sepsis()
    else:
        print("No valid input. Try again!\n")
        main()


main()