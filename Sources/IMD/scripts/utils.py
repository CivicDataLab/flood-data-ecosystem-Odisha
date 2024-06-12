import os

import pandas as pd


def keep_columns_in_csv(input_folder, output_folder, columns_to_keep):
    # Ensure the output folder exists
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Loop through all files in the input folder
    for filename in os.listdir(input_folder):
        # Check if the file is a CSV file
        if filename.endswith(".csv"):
            file_path = os.path.join(input_folder, filename)
            df = pd.read_csv(file_path)

            # Keep only the specified columns
            df = df[columns_to_keep]

            # Save the modified CSV to the output folder
            output_path = os.path.join(output_folder, filename)
            df.to_csv(output_path, index=False)
            print(f"Processed {filename}")


# Specify the input folder containing the CSV files
input_folder = "path/to/your/input/folder"

# Specify the output folder where the modified CSV files will be saved
output_folder = "path/to/your/output/folder"

# Specify the columns to keep
columns_to_keep = ["id", "max", "mean", "count", "sum"]

# Call the function
keep_columns_in_csv(input_folder, output_folder, columns_to_keep)
