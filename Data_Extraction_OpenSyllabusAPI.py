#%%

import os
import requests
import pandas as pd
import warnings
from pandas import json_normalize
from tabulate import tabulate
import json

warnings.filterwarnings('ignore')


#%%


# API endpoints and query params

query_param_dict = {
    1: "syllabi",
    2: "titles",
    3: "institutions",
    4: "fields",
    5: "countries",
    6: "publishers"
}


query_param_required = int(input(f"Enter the number({', '.join([f'{k}: {v}' for k, v in query_param_dict.items()])}):\n"))
print(query_param_dict[query_param_required])

#%%


#
url = 'https://api.opensyllabus.org/analytics/v1/' + str(query_param_dict[query_param_required]) + '?size=2000'
api_key = str(input((f"Enter the API key:")))

# Send GET request with API key
response = requests.get(url, headers={'Authorization': f'Api-Key {api_key}'})

# Check the response
if response.status_code == 200:
    print(response)
else:
    print(f"Failed to fetch data: {response.status_code} - {response.text}")



#%%



df = pd.read_json(response.text)
#df2 = json.loads(df.iloc[0, 1])

col_required_to_extract = { 'syllabi': 1, 'titles': 3, 'fields': 1}


#%%

column_index = col_required_to_extract[query_param_dict[query_param_required]]
os_data_raw = pd.json_normalize(df.iloc[:, int(column_index) ])


print(f"First 5 observations: \n{os_data_raw.head()}")
print(f"The features are : \n {os_data_raw.columns.values}")

#os_data_raw.to_csv("OS_Syllabi_Exported_Data_from_API.csv")

#%%


os_df = pd.read_json(response.text)

def convert_and_flatten(x):
    if isinstance(x, str):
        try:
            x = json.loads(x)  # Convert string to dict
        except json.JSONDecodeError:
            return x
    if isinstance(x, dict):
        return pd.json_normalize(x).iloc[0]  # Flatten dict to single row
    return x

# Apply to column 1 only
expanded = df.iloc[:, column_index].apply(convert_and_flatten)

# Combine with original DataFrame (keeping other columns)
os_df_structured = pd.concat([os_df.drop(df.columns[column_index], axis=1), expanded], axis=1)


print(f"{os_df_structured.head()}")

#%%
# Convert lists and dicts to strings
os_df_mapped = os_df_structured.applymap(lambda x: str(x) if isinstance(x, (list, dict)) else x)

# Now drop duplicates
os_df_mapped = os_df_mapped.drop_duplicates()
os_df_mapped.to_csv("OS_" + str(query_param_dict[query_param_required]) + "_Exported_Data_from_API.csv")
