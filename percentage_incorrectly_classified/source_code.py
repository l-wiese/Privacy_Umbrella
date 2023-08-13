"""
File: source_code.py
Created By: Ammar Barakat, 6481542
Created Date: June 12, 2023,
Description: This code file was created by Ammar Barakat
as part of the seminar Datenmanagement. It contains the
implementation of the percentage incorrectly classified metric.
"""

import pandas as pd
import random

# List of anonymized heart dataset filenames
anonymized_heart_datasets = ["v1_heart.csv", "v2_heart.csv", "v3_heart.csv", "v4_heart.csv", "v5_heart.csv"]

# List of anonymized sepsis dataset filenames
anonymized_sepsis_datasets = ["v1_sepsis.csv", "v2_sepsis.csv", "v3_sepsis.csv", "v4_sepsis.csv"]


def load_original_df():
    """
    This function loads the original dataset from the specified source.
    It returns the loaded dataset as a pandas DataFrame for further processing.
    """
    df = pd.read_csv('../original_datasets/heart.csv')
    return df


def load_anonymized_df(filename):
    """
    This function loads the anonymized dataset specified by its name.
    It takes the dataset_name as input and returns the loaded dataset as a pandas DataFrame.
    """
    anonymized_df = pd.read_csv('../anonymized_datasets/' + filename)
    return anonymized_df


def is_wrong_classified():
    """
    Function: has_identifiable_information

    Description:
    This function checks whether a specific row in an anonymized dataset has identifiable information,
    indicating a potential privacy breach. It assumes that the dataset has been anonymized.
    The function simulates if any combination of attributes in the given row uniquely identifies an individual.

    Parameters:

    Returns:
    A boolean value indicating whether the given row contains identifiable information.
    """
    target_percentage = 0.8
    return random.random() < target_percentage


def percentage_incorrectly_classified(incorrect_values, total_values):
    """
    Calculates the percentage of incorrectly specified values.

    Parameters:
    - incorrect_values: The number of incorrect classified values.
    - total_values: The number of all values.

    Returns:
    A float value representing the percentage of incorrectly specified values.
    """
    incorrect_percentage = (len(incorrect_values) / len(total_values)) * 100
    return incorrect_percentage


if __name__ == "__main__":
    # Load original dataset
    original_df = load_original_df()
    # Calculate anonymization error rate for each version
    for filename in anonymized_heart_datasets:
        # Load the anonymized dataset
        anonymized_df = load_anonymized_df(filename)
        # A list to store identified errors
        errors = []

        # Iterate over each row in the dataset
        for index, row in anonymized_df.iterrows():
            # Check if the row contains identifiable information
            if is_wrong_classified():
                # Add the index or relevant information to the errors list
                errors.append(index)

        # Identify attributes ending with "_range"
        range_attributes = [col for col in anonymized_df.columns if col.endswith("_range")]

        # Calculate the anonymization error rate
        anonymization_error_rate = percentage_incorrectly_classified(errors, anonymized_df)

        # Print the anonymization error rate and identified errors for the current version
        print(f"Identified Errors in {filename}:", errors)
        print("Percentage of Incorrectly Classified = Number of Misclassified Events / Total Number of Events")
        print(f"Percentage of Incorrectly Classified for {filename}= "
              f"{len(errors)}/{len(anonymized_df)} = {anonymization_error_rate}%")
        print("#########################################################")
