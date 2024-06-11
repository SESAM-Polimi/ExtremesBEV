#%%
from fiona.core.db_builder import DB_builder
import json

user = 'LR'

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
