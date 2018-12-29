import pandas as pd
import re

def main():
    servant_survey_df = pd.read_csv("data/Google Sheets csv/SSR NA complete test October 2018 (respuestas) - Respuestas de formulario 1.csv", mangle_dupe_cols=True)

    #These records are Paid Gacha or 100-300 but record values in the columns for F2P
    servant_survey_df = servant_survey_df.drop([5])

    splitted_df = {}

    for money_type in servant_survey_df['How much money have you used in-game?'].unique():
        splitted_df[money_type] = servant_survey_df[servant_survey_df['How much money have you used in-game?'] == money_type]

    PROPER_COLUMNS_NAME = ['Time', 'Money Spent', 'Saber', 'Archer', 'Lancer', 'Rider', 'Caster', 'Assassin', 'Berserker', 'Ruler', 'Avenger']

    #Each player type servant data are recorded in different columns for different player type.
    #Eg: F2P Sabers in 'SSR Sabers'; Paid Gacha Sabers in 'SSR Sabers.1' and so on
    #Therefore, if NA columns are removed, only columns of the relevant player type remain
    for player_type, player_df in splitted_df.items():
        splitted_df[player_type] = player_df.dropna(axis = 1, how = 'all').iloc[:,:17]
        splitted_df[player_type].columns = PROPER_COLUMNS_NAME

    servant_class_list = {}

    #Use whale dataset to make sure we don't miss any servant
    for servant_class in PROPER_COLUMNS_NAME[2:11]:
        servant_class_list[servant_class] = list(splitted_df['501 USD and onwards'][servant_class].dropna().unique())

    #Get servant list for each class
    for servant_class, servant_list in servant_class_list.items():
        servant_class_list[servant_class] = list({str(ssr).strip() for item in servant_list for ssr in item.split(',')})
        servant_class_list[servant_class].sort()

    #Create servants' columms containing TRUE or FALSE
    for player_type, player_df in splitted_df.items():
        for servant_class in servant_class_list:
            for servant in servant_class_list[servant_class]:
                splitted_df[player_type][servant] = player_df[servant_class].str.contains(re.escape(servant), na = False)

    merged_survey_df = pd.DataFrame()

    for player_type, player_df in splitted_df.items():
        splitted_df[player_type]['Money Spent'] = player_type
        merged_survey_df = merged_survey_df.append(splitted_df[player_type])

    merged_survey_df = merged_survey_df.drop(columns = PROPER_COLUMNS_NAME[2:11])

    merged_survey_df.to_csv("data/merged_df.csv", index_label='index')

    # for player_type, player_df in splitted_df.items():
    #     player_df.to_csv("data/{}.csv".format(player_type))

    servant_class_table = [(servant, servant_class) for servant_class in servant_class_list for servant in servant_class_list[servant_class]]
    servant_df = pd.DataFrame(servant_class_table, columns=['Servant', 'Class'])

    #This data set doesn't contain limitted data though so that has to be inputted manually at the moment
    servant_df.to_csv('data/servant.csv', index=False)

if __name__ == '__main__':
    main()
