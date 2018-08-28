import pandas as pd
import re

def main():
    servant_survey_df = pd.read_csv("data/Resultados Agosto summer - Respuestas de formulario 1.csv", mangle_dupe_cols=True)

    #These records are Paid Gacha or 100-300 but record values in the columns for F2P
    servant_survey_df = servant_survey_df.drop([478, 1324, 1973, 2195])

    splitted_df = {}

    splitted_df['F2P']              = servant_survey_df[servant_survey_df['How much money have you used in-game?'] == 'F2P']
    splitted_df['Paid Gacha']       = servant_survey_df[servant_survey_df['How much money have you used in-game?'] == 'Paid Gacha Only']
    splitted_df['$1-100 monthly']   = servant_survey_df[servant_survey_df['How much money have you used in-game?'] == 'More than 1USD but less than 100 Monthly']
    splitted_df['$100-300 monthly'] = servant_survey_df[servant_survey_df['How much money have you used in-game?'] == 'More than 100USD but less than 300 Monthly']
    splitted_df['$300-500 monthly'] = servant_survey_df[servant_survey_df['How much money have you used in-game?'] == 'More than 300USD but less than 500 Montlhy']
    splitted_df['$500- monthly']    = servant_survey_df[servant_survey_df['How much money have you used in-game?'] == 'More than 500 Monthly']

    PROPER_COLUMNS_NAME = ['Time', 'Money Spent', 'Sabers', 'Archers', 'Lancers', 'Riders', 'Casters', 'Assassins', 'Berserkers', 'Rulers', 'Avengers']

    #Each player type servant data are recorded in different columns for different player type.
    #Eg: F2P Sabers in 'SSR Sabers'; Paid Gacha Sabers in 'SSR Sabers.1' and so on
    #Therefore, if NA columns are removed, only columns of the relevant player type remain
    for player_type, player_df in splitted_df.items():
        splitted_df[player_type] = player_df.dropna(axis = 1, how = 'all').iloc[:,:11] #only care about servants stats
        splitted_df[player_type].columns = PROPER_COLUMNS_NAME

    servant_class_list = {}

    #Use whale dataset to make sure we don't miss any servant
    for servant_class in PROPER_COLUMNS_NAME[2:]:
        servant_class_list[servant_class] = list(splitted_df['$500- monthly'][servant_class].dropna().unique())

    #Get servant list for each class
    for servant_class, servant_list in servant_class_list.items():
        servant_class_list[servant_class] = list({str(ssr).strip() for item in servant_list for ssr in item.split(',')})

    #Create servants' columms containing TRUE or FALSE
    for player_type, player_df in splitted_df.items():
        for servant_class in servant_class_list:
            for servant in servant_class_list[servant_class]:
                splitted_df[player_type][servant] = player_df[servant_class].str.contains(re.escape(servant), na = False)

    merged_survey_df = pd.DataFrame()

    for player_type, player_df in splitted_df.items():
        splitted_df[player_type]['Money Spent'] = player_type
        merged_survey_df = merged_survey_df.append(splitted_df[player_type])

    merged_survey_df = merged_survey_df.drop(columns = (PROPER_COLUMNS_NAME[2:] + ['Extra Option: Angra Mainyu']))

    merged_survey_df.to_csv("data/merged_df.csv", index_label='index')

    # for player_type, player_df in splitted_df.items():
    #     player_df.to_csv("data/{}.csv".format(player_type))

    servant_class_list['Avenger'].remove('Extra Option: Angra Mainyu')

    servant_class_table = [(servant, servant_class) for servant_class in servant_class_list for servant in servant_class_list[servant_class]]
    servant_df = pd.DataFrame(servant_class_table, columns=['Servant', 'Class'])

    #This data set doesn't contain limitted data though so that has to be inputted manually at the moment
    servant_df.to_csv('data/servant.csv', index=False)

if __name__ == '__main__':
    main()
