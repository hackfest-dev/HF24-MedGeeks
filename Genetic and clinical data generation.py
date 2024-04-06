import random
import pandas as pd
import streamlit as st

def generate_data(num_entries):
    """
    Simulates generating data for ovarian cancer sub-types, stages, and additional factors.

    Args:
        num_entries: The number of entries to generate.

    Returns:
        A list of dictionaries, where each dictionary represents an entry
        with the following keys:
            - sub_type (str): The ovarian cancer sub-type (epithelial, germcell, stromal)
            - stage (str): The ovarian cancer stage (stage-0, stage-1, ..., stage-4)
            - age (int): The patient's age
            - genetic_changes_brca (str): Yes or No
            - genetic_changes_rad51 (str): Yes or No
            - family_history (str): Yes or No
            - early_periods (str): Yes or No
            - late_menopause (str): Yes or No
            - never_pregnant (str): Yes or No
            - childbirth_history (str): Yes or No
            - smoking (str): Yes or No
            - overweight_or_obese (str): Yes or No
            - hormone_replacement_therapy (str): Yes or No
            - endometriosis (str): Yes or No
            - outlier (str): Yes or No
    """
    data = []
    for _ in range(num_entries):
        # Generate sub-type based on probability
        sub_type_probs = [0.52, 0.24, 0.24]  # Epithelial, GermCell, Stromal
        sub_type = random.choices(
            ["epithelial", "germcell", "stromal"], sub_type_probs)[0]

        # Generate age based on sub-type
        if sub_type == "epithelial":
            if random.random() < 0.1:  # Less likely under 40
                age = random.randint(20, 39)
            else:
                age = random.randint(40, 80)
        elif sub_type == "germcell":
            age = random.randint(20, 70)  # More evenly distributed
        else:  # Stromal
            if random.random() > 0.63:  # More likely above 63
                age = random.randint(64, 80)
            else:
                age = random.randint(40, 63)

        # Generate stage based on age
        stage = None
        if age < 40:
            stage = "stage-1"
        elif 40 <= age <= 50:
            stage = random.choice(["stage-2", "stage-3"])
        elif 51 <= age <= 65:
            stage = random.choice(["stage-2", "stage-3", "stage-4"])
        else:
            stage = random.choice(["stage-3", "stage-4"])

        # Generate other factors
        genetic_changes_brca = random.choice(["Yes", "No"])
        genetic_changes_rad51 = random.choice(["Yes", "No"])
        family_history = random.choice(["Yes", "No"])
        early_periods = random.choice(["Yes", "No"])
        late_menopause = random.choice(["Yes", "No"])
        never_pregnant = random.choice(["Yes", "No"])
        childbirth_history = random.choice(["Yes", "No"])
        smoking = random.choice(["Yes", "No"])
        overweight_or_obese = random.choice(["Yes", "No"])
        hormone_replacement_therapy = random.choice(["Yes", "No"])
        endometriosis = random.choice(["Yes", "No"])

        # Generate outlier
        outlier = random.choice(["Yes", "No"])

        data.append({
            "sub_type": sub_type,
            "stage": stage,
            "age": age,
            "genetic_changes_brca": genetic_changes_brca,
            "genetic_changes_rad51": genetic_changes_rad51,
            "family_history": family_history,
            "early_periods": early_periods,
            "late_menopause": late_menopause,
            "never_pregnant": never_pregnant,
            "childbirth_history": childbirth_history,
            "smoking": smoking,
            "overweight_or_obese": overweight_or_obese,
            "hormone_replacement_therapy": hormone_replacement_therapy,
            "endometriosis": endometriosis,
            "outlier": outlier
        })
    return data
data = generate_data(500)
df = pd.DataFrame(data)

# Save the DataFrame to an Excel file
df.to_excel("ovarian_cancer_data_with_factors_and_outliers.xlsx", index=False)

# Display the DataFrame
st.write(df)
