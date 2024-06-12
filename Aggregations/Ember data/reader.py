# -*- coding: utf-8 -*-
"""
Created on Fri Dec  1 12:29:19 2023

@author: loren
"""

#%%
import pandas as pd

paths = {
    'Electricity': {
        'name': "yearly_full_release_long_format.csv",
        'country': 'Country code',
        'year': 'Year',
        'variable': ['Bioenergy','Coal','Gas','Hydro','Nuclear','Other Fossil','Other Renewables','Solar','Wind'],
        },
    }


#%%
data = {name:pd.read_csv(path['name']) for name,path in paths.items()}
countries = {name: sorted([x for x in list(set(df[paths[name]['country']])) if str(x) != 'nan']) for name,df in data.items()}
years = {name: sorted([x for x in list(set(df[paths[name]['year']])) if str(x) != 'nan']) for name,df in data.items()}

exio_countries = pd.read_excel('ExioEmber.xlsx',sheet_name='Countries',index_col=[0])

#%%
ee_mixes = {}
name = 'Electricity'
variable = 'variable'

for year in years[name]:
    ee_mixes[year] = pd.DataFrame()
    for country in countries[name]:
        ee_production = data[name].query(f"`{paths[name]['country']}`=='{country}' & Variable in {paths[name][variable]} & Year==@year & Category=='Electricity generation' & Unit=='TWh'")
        ee_production = ee_production.set_index(['Variable']).loc[:,'Value'].to_frame()
        ee_production.columns = [exio_countries.loc[country,'Exiobase']]
        ee_mixes[year] = pd.concat([ee_mixes[year], ee_production], axis=1)
    
    ee_mixes[year] = ee_mixes[year].fillna(0)
    ee_mixes[year] = ee_mixes[year].groupby(level=0, axis=1).sum()
    ee_mixes[year] /= ee_mixes[year].sum(0)

#%%
writer = pd.ExcelWriter('EE mixes Ember-Exiobase.xlsx')
for year,mix in ee_mixes.items():
    mix.T.to_excel(writer,sheet_name=str(year))
writer.close()

