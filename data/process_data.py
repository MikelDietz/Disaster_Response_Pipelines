import sys
import numpy as np
import pandas as pd
from sqlalchemy import create_engine
 

def load_data(messages_filepath, categories_filepath):
    """
    Load Data Function 
    Arguments:
        Messages filepath  -> Filepath of the messages dataset
        Categories filepath -> Filepath of the Categories datset 
    Output:
        df -> Merged dataframe by id (messages and categories data) 
    """
    #read csv s 
    messages = pd.read_csv(messages_filepath) 
    
    # load categories dataset
    categories = pd.read_csv(categories_filepath)
   
    # merge datasets
    df =  messages.merge(categories, on= 'id', how = 'inner')
    
    return df


def clean_data(df):
    """
    Clean Data Function 
    Arguments:
        Df -> Dataframe of messages and categories data 
    Output: 
        Df -> Cleaned and transformed data
    """
    #create df of 36 individual category columns 
    categories = df.categories.str.split(pat=';', expand=True)

    # select the first row of the categories dataframe
    row = categories.iloc[0]
    category_colnames = row.apply(lambda x: x[:-2]).values.tolist()

    # rename the columns of 'categories'
    categories.columns = category_colnames

    #convert category values to just numbers 0 or 1.
    for column in categories:
        # set each value to be the last character of the string
        categories[column] = categories[column].astype(str).str[-1:]

        # convert column from string to numeric
        categories[column] = categories[column].astype(np.int)

    #replace 'categories' column in 'df' with new category columns.
    # drop the original categories column from 'df'
    df.drop('categories',axis=1)

    # concatenate the original dataframe with the new `categories` dataframe
    df = pd.concat([df,categories], join='inner', axis=1)
    
    # drop duplicates
    df = df.drop_duplicates(subset = 'id')
    
    # set labels in the 'related' category to binary 
    df.loc[df['related'] > 1,'related'] = 0  

    return df


def save_data(df, database_filename):
    """
    Save Data Function 
    Arguments: 
        DF -> Messages and Categories dataframe
        Database Filename -> The file name we want to call it 
    """
    engine = create_engine('sqlite:///'+ database_filename)
    df.to_sql(name = 'DisasterResponse', con = engine, index=False, if_exists = 'replace')
    


def main():
    if len(sys.argv) == 4:

        messages_filepath, categories_filepath, database_filepath = sys.argv[1:]

        print('Loading data...\n    MESSAGES: {}\n    CATEGORIES: {}'
              .format(messages_filepath, categories_filepath))
        df = load_data(messages_filepath, categories_filepath)

        print('Cleaning data...')
        df = clean_data(df)
        
        print('Saving data...\n    DATABASE: {}'.format(database_filepath))
        save_data(df, database_filepath)
        
        print('Cleaned data saved to database!')
    
    else:
        print('Please provide the filepaths of the messages and categories '\
              'datasets as the first and second argument respectively, as '\
              'well as the filepath of the database to save the cleaned data '\
              'to as the third argument. \n\nExample: python process_data.py '\
              'disaster_messages.csv disaster_categories.csv '\
              'DisasterResponse.db')


if __name__ == '__main__':
    main()
