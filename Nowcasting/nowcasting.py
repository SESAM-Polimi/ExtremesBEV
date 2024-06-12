#%%
import pandas as pd
import mario
from mario.tools.constants import _MASTER_INDEX as MI
import requests

base_url = "https://api.ember-climate.org"
api = '3a8a244b-de18-48de-ac37-e4e5f83b9c9a'
ember_series = ['Bioenergy','Coal','Gas','Hydro','Nuclear','Other fossil','Other renewables','Solar','Wind']
sn = slice(None)

def get_yearly_ember_mixes_by_country(
        country_map_path:str,
        database_name:str,
        year:float,
        ):

    query_url = (
        f"{base_url}/v1/electricity-generation/yearly"
        + f"?&is_aggregate_series=false&start_date={year}&api_key={api}"
        )
    
    response = requests.get(query_url)

    if response.status_code == 200:
        data = response.json()
    
    data = data['data']

    country_map = pd.read_excel(country_map_path, index_col=[0])[database_name].to_frame()
    country_map = {i:country_map.loc[i,database_name] for i in country_map.index}
    countries = list(country_map.keys())

    ee_mix_data = pd.DataFrame(0,index=countries,columns=ember_series)
    for k in data:
        if k['entity_code'] is not None:
            if k['entity_code'] not in countries or k['series'] not in ember_series:
                continue
            else:
                ee_mix_data.loc[k['entity_code'],k['series']] = k['generation_twh']

    ee_mix_data.index.names = ['Countries']
    ee_mix_data.reset_index(inplace=True)

    ee_mix_data['Database countries'] = ee_mix_data['Countries'].map(country_map)
    ee_mix_data.set_index('Database countries',inplace=True)
    ee_mix_data.drop('Countries',axis=1,inplace=True)
    ee_mix_data = ee_mix_data.groupby(level=0).sum()

    ee_mix_data = ee_mix_data.div(ee_mix_data.sum(axis=1), axis=0)

    return ee_mix_data

#%%
def ee_mixes_update(
        instance,
        ee_mix_data,
        ee_commodity:str='Electricity',
        scenario:str='baseline',
    ):

    z = instance.get_data(['z'],scenarios=[scenario])[scenario][0]
    s = z.loc[(sn,MI['a'],sn),(sn,MI['c'],sn)]
    other_activities = [i for i in instance.get_index(MI['a']) if i not in ember_series]

    for country in ee_mix_data.index:
        print(country)
        df_mix = ee_mix_data.loc[country,:]
        if isinstance(df_mix,pd.Series):
            df_mix = df_mix.to_frame()
        else:
            df_mix = df_mix.T
        
        df_mix.columns = pd.MultiIndex.from_arrays([[country],[MI['c']],[ee_commodity]])
        df_mix.index = pd.MultiIndex.from_arrays(
            [[country for i in ember_series],[MI['a'] for i in ember_series], list(df_mix.index)]
        )

        other_ee_production = s.loc[(sn,sn,other_activities),(country,MI['c'],ee_commodity)].sum().sum()
        total_ee_production = s.loc[:,(country,MI['c'],ee_commodity)].sum().sum()
        df_mix *= total_ee_production-other_ee_production

        s.update(df_mix)
    
    z.update(s)

    instance.update_scenarios(scenario=scenario,z=z)
    instance.reset_to_coefficients(scenario=scenario)

    return instance



        




#%%
# data = {name:pd.read_csv(path['name']) for name,path in paths.items()}
# countries = {name: sorted([x for x in list(set(df[paths[name]['country']])) if str(x) != 'nan']) for name,df in data.items()}
# years = {name: sorted([x for x in list(set(df[paths[name]['year']])) if str(x) != 'nan']) for name,df in data.items()}

# exio_countries = pd.read_excel('ExioEmber.xlsx',sheet_name='Countries',index_col=[0])

# #%%
# ee_mixes = {}
# name = 'Electricity'
# variable = 'variable'

# for year in years[name]:
#     ee_mixes[year] = pd.DataFrame()
#     for country in countries[name]:
#         ee_production = data[name].query(f"`{paths[name]['country']}`=='{country}' & Variable in {paths[name][variable]} & Year==@year & Category=='Electricity generation' & Unit=='TWh'")
#         ee_production = ee_production.set_index(['Variable']).loc[:,'Value'].to_frame()
#         ee_production.columns = [exio_countries.loc[country,'Exiobase']]
#         ee_mixes[year] = pd.concat([ee_mixes[year], ee_production], axis=1)
    
#     ee_mixes[year] = ee_mixes[year].fillna(0)
#     ee_mixes[year] = ee_mixes[year].groupby(level=0, axis=1).sum()
#     ee_mixes[year] /= ee_mixes[year].sum(0)

# #%%
# writer = pd.ExcelWriter('EE mixes Ember-Exiobase.xlsx')
# for year,mix in ee_mixes.items():
#     mix.T.to_excel(writer,sheet_name=str(year))
# writer.close()

