from server import functions_basic
import re
import numpy as np

def normalizeAndNumericalize(df__acceptance, df__actions, df__app_names, df__location, df__sex, df__weekdays, df_user_app_usage, df_users):
    # df_user_app_usage
    df_user_app_usage_normalized = df_user_app_usage.drop(columns=['id', 'created_at'])
    df_user_app_usage_normalized = functions_basic.one_hot_encoding(df_user_app_usage_normalized, df__weekdays, 'weekday', 'id', 'weekday')
    df_user_app_usage_normalized = functions_basic.normalize_time(df_user_app_usage_normalized, 'time_of_day')
    df_user_app_usage_normalized = functions_basic.normalize_numerical_data(df_user_app_usage_normalized, 'app_usage_time', fixed_max=86400) # 24h max
    df_user_app_usage_normalized = functions_basic.hash_encode(df_user_app_usage_normalized, 'app_name', 1000) # hash-encoding upto 1000 apps
    df_user_app_usage_normalized = functions_basic.one_hot_encoding(df_user_app_usage_normalized, df__acceptance, 'acceptance', 'id', 'acceptance')
    df_user_app_usage_normalized = functions_basic.one_hot_encoding(df_user_app_usage_normalized, df__actions, 'action', 'id', 'action')
    df_user_app_usage_normalized = functions_basic.one_hot_encoding(df_user_app_usage_normalized, df__location, 'location', 'id', 'location')
    df_user_app_usage_normalized = functions_basic.convert_boolean_to_numeric(df_user_app_usage_normalized, 'should_be_blocked')

    # df_users
    df_users_normalized = functions_basic.convert_string_to_date(df_users, 'date_of_birth')
    df_users_normalized = df_users_normalized.drop(columns=['created_at', 'date_of_birth', 'first_name', 'last_name'])
    df_users_normalized = functions_basic.normalize_numerical_data(df_users_normalized, 'age', fixed_max=130) # max-age fixed to 130 years
    df_users_normalized = functions_basic.one_hot_encoding(df_users_normalized, df__sex, 'sex', 'id', 'sex')

    return df_user_app_usage_normalized, df_users_normalized

def mergeUsersAndAppUsage(df_user_app_usage_normalized, df_users_normalized):
    merged_df = df_users_normalized.merge(df_user_app_usage_normalized, left_on='id', right_on='user_id')
    merged_df = functions_basic.hash_encode(merged_df, 'user_id', 1000) # hash-encoding upto 1000 users

    merged_df = merged_df.drop(columns=['id'])
    merged_df = functions_basic.set_column_data_types(merged_df)
    
    return merged_df


def clearAndResetMissingColumnsInApp(df_original):
    df = df_original.copy()
    
    # To clear
    patterns_to_clear = ['acceptance_.*', 'action_.*'] # Patterns for columns to be dropped
    columns_matching_patterns = [col for col in df.columns if any(re.match(pattern, col) for pattern in patterns_to_clear)] # Find columns that match the patterns

    # Drop and clear the columns
    df = df.drop(columns=['should_be_blocked'], errors='ignore') # Ignore if should_be_blocked column doe snot exist
    df[columns_matching_patterns] = False
    df['app_usage_time'] = 0
    
    df['app_usage_time'] = df['app_usage_time'].astype('float32')
    
    return df

def clearAndResetMissingColumnsInTraining(data_dict):
    # To clear
    patterns_to_clear = ['acceptance_.*', 'action_.*']  # Patterns for columns to be dropped

    # Process each array in the dictionary
    for key in data_dict.keys():
        if any(re.match(pattern, key) for pattern in patterns_to_clear):
            # Set all values in matching columns to False
            data_dict[key] = np.array([False] * len(data_dict[key]), dtype='bool')
        elif key == 'app_usage_time':
            # Set all values in 'app_usage_time' to 0
            data_dict[key] = np.array([0.0] * len(data_dict[key]), dtype='float32')

    return data_dict