import pandas as pd
from datetime import datetime
import glob

# Define new column names mapping
new_column_names = {
    'ID': 'CitizenID',
    'Block Type': 'BlockType',
    'Blocked Channel [ติดต่อทางโทรศัพท์]': 'ChannelTELE',
    'Blocked Channel [Direct Mail]': 'ChannelDM',
    'Blocked Channel [SMS]': 'ChannelSMS',
    'Blocked Channel [Email]': 'ChannelMAIL'
}

# Specify the directory where your Excel files are located
directory_path = "/workspaces/block_channel/mockup data/*.xlsx"

# Get a list of all Excel files in the specified directory
excel_files = glob.glob(directory_path)

uploaded_dfs = []
for file_name in excel_files:
    df = pd.read_excel(file_name)
    
    # Keep only the first character in columns 3 to 6
    df.iloc[:, 3:7] = df.iloc[:, 3:7].astype(str).applymap(lambda x: x[0])

    # Remove specified columns by index
    columns_to_remove = [1, 7, 8, 9, 10, 11, 12]  # Indices of columns to remove
    df = df.drop(df.columns[columns_to_remove], axis=1)
    
    # Add new column 'EffectiveDate' with current date (YYYYMMDD)
    df['EffectiveDate'] = datetime.now().strftime('%Y%m%d')
    
    uploaded_dfs.append(df)

# Rename columns for each uploaded DataFrame
for df in uploaded_dfs:
    df.rename(columns=new_column_names, inplace=True)

# Define a function to check conditions for a DataFrame
def check_conditions(df, file_name):
    # Check conditions
    conditions_met = True
    # Check Block Type
    if 'BlockType' in df.columns:
        df['BlockType'] = df['BlockType'].str.strip().str.upper()
        if not df['BlockType'].isin(['SPD', 'GPD']).all():
            print(f"Error: Invalid 'Block Type' values found in {file_name}.")
            conditions_met = False
    else:
        print(f"Error: 'Block Type' column not found in {file_name}.")

    # Check CHANNEL_TELE
    if 'ChannelTELE' in df.columns:
        if not df['ChannelTELE'].astype(str).str.strip().str.match(r'^[0-3]$').all():
            print(f"Error: Invalid 'ChannelTELE' values found in {file_name}.")
            conditions_met = False
    else:
        print(f"Error: 'Channel' column not found in {file_name}.")

    # Check CHANNEL_DM, CHANNEL_SMS, CHANNEL_MAIL
    for channel in ['ChannelDM', 'ChannelSMS', 'ChannelMAIL']:
        if channel in df.columns:
            if not df[channel].astype(str).str.strip().str.match(r'^[01]$').all():
                print(f"Error: Invalid values found in '{channel}' column in {file_name}.")
                conditions_met = False
        else:
            print(f"Error: '{channel}' column not found in {file_name}.")

    return df, conditions_met

# Check conditions for each uploaded DataFrame
conditions_met = []
for i, uploaded_df in enumerate(uploaded_dfs):
    uploaded_df, conditions = check_conditions(uploaded_df, excel_files[i])
    conditions_met.append(conditions)

# Export the DataFrames to .txt files with pipe delimiter if conditions are met for both files
if all(conditions_met):
    concatenated_data = pd.concat(uploaded_dfs, ignore_index=True)
    concatenated_data.to_csv('concatenated_data.txt', sep='|', index=False)
    print("Files concatenated successfully.")
elif sum(conditions_met) == 1:
    index_of_met_condition = conditions_met.index(True)
    single_condition_met_df = uploaded_dfs[index_of_met_condition]
    single_condition_met_df.to_csv(f'{excel_files[index_of_met_condition]}.txt', sep='|', index=False)
    print(f"Single file '{excel_files[index_of_met_condition]}' exported successfully.")
else:
    for i, conditions in enumerate(conditions_met):
        if not conditions:
            print(f"Error: Conditions not met for '{excel_files[i]}'.")