#%%
from fiona.core.db_builder import DB_builder
import json
import pandas as pd

user = 'DG'

with open('Paths.json', 'r') as file:
    paths = json.load(file)[user]


#%%
sut_mode = 'coefficients'

db = DB_builder(
    sut_path=paths['Exiobase']+f"\{sut_mode}",
    sut_mode=sut_mode,
    master_file_path=paths['FIONA Master'],
    sut_format='txt',
    read_master_file=False,
)

# %%
nowcasting_year = 2023

db.sut.aggregate("Aggregations/1. Nowcasting electricity.xlsx",ignore_nan=True)

#%%
ee_mixes = pd.read_excel("Data/EE mixes Ember-Exiobase.xlsx" ,sheet_name=str(nowcasting_year),index_col=[0])




# %%
