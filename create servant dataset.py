import pandas as pd

servant_survey_df = pd.read_csv("data/Resultados Agosto summer - Respuestas de formulario 1.csv", mangle_dupe_cols=True)

#Copied from the create player datasets file. Probably should have written a function

#The "[..-..]" part in Waver's name will cause trouble with regex later
servant_survey_df = servant_survey_df.replace("Zhuge Liang \[El\-Melloi II\]", "Zhuge Liang", regex = True)

splitted_df = {}

splitted_df['$500- monthly']    = servant_survey_df[servant_survey_df['How much money have you used in-game?'] == 'More than 500 Monthly']

PROPER_COLUMNS_NAME = ['Time', 'Money Spent', 'Saber', 'Archer', 'Lancer', 'Rider', 'Caster', 'Assassin', 'Berserker', 'Ruler', 'Avenger']

for player_type, player_df in splitted_df.items():
    splitted_df[player_type] = player_df.dropna(axis = 1, how = 'all').iloc[:,:11] #only caree about servants stats
    splitted_df[player_type].columns = PROPER_COLUMNS_NAME

servant_class_list = {}

#Use whale dataset to make sure we don't miss any servant
for servant_class in PROPER_COLUMNS_NAME[2:]:
    servant_class_list[servant_class] = list(splitted_df['$500- monthly'][servant_class].dropna().unique())

for servant_class, servant_list in servant_class_list.items():
    servant_class_list[servant_class] = list({ssr.strip() for item in servant_list for ssr in item.split(',')})

servant_class_list['Avenger'].remove('Extra Option: Angra Mainyu')

servant_df = pd.DataFrame([(servant, servant_class) for servant_class in servant_class_list for servant in servant_class_list[servant_class]], columns=['Servant', 'Class'])

#This data set doesn't contain limitted data though so that has to be inputted manually at the moment
servant_df.to_csv('data/servant.csv', index=False)