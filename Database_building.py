#%%
from fiona.core.db_builder import DB_builder
import mario
import json
import pandas as pd
from Nowcasting.nowcasting import get_yearly_ember_mixes_by_country,ee_mixes_update

user = 'LR'
nowcasting_year = 2022
sut_mode = 'coefficients'

with open('Paths.json', 'r') as file:
    paths = json.load(file)[user]

#%% parse Exiobase
db = mario.parse_from_txt(paths['Exiobase']+f"\{sut_mode}",mode='flows',table='SUT')

#%% aggregate Exiobase
db.aggregate("Aggregations/1. Nowcasting electricity.xlsx",ignore_nan=True)

#%%
ee_mixes = get_yearly_ember_mixes_by_country(
    country_map_path = paths['EMBER']['countries map'],
    database_name='Exiobase',
    year=nowcasting_year
    )

# %%
db = ee_mixes_update(db,ee_mixes)

# %%
db = DB_builder(
    sut_path=db,
    sut_mode=sut_mode,
    master_file_path=paths['FIONA Master'],
    sut_format='txt',
    read_master_file=False,
)