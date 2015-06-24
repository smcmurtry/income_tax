
# coding: utf-8

### Cleaning Historical Data

# In[20]:

import pandas as pd
import urllib
import os


# In[4]:

tax_by_income_url = {2008: "http://www.cra-arc.gc.ca/gncy/stts/gb08/pst/fnl/csv/t02ca.csv",
                     2009: "http://www.cra-arc.gc.ca/gncy/stts/gb09/pst/fnl/csv/t02ca.csv",
                     2010: "http://www.cra-arc.gc.ca/gncy/stts/gb10/pst/fnl/csv/t02ca.csv",
                     2011: "http://www.cra-arc.gc.ca/gncy/stts/gb11/pst/fnl/csv/t02ca.csv",
                     2012: None}


# In[21]:

def delete_extra_cols(df):
    columns2delete = [col for col in df.columns if '_r' in col or '_l' in col or 'Unnamed' in col] 
    for col in columns2delete: del df[col]
    return df

def clean_the_df(rough_df, header_lines):
    length_of_dataframe = header_lines[1] - 1
    temp_filenames = []
    for n, i in enumerate(header_lines):
        filename = '../data/test_' + str(n) + '.csv'
        if n == 0:
            rough_df[i:length_of_dataframe].to_csv(filename, index=False)
        else:
            rough_df[i-1:i+length_of_dataframe].to_csv(filename, header=False, index=False)
        temp_filenames.append(filename)

    for n, filename in enumerate(temp_filenames):
        if n == 0: clean_df = pd.DataFrame.from_csv(filename, index_col=None)
        else: clean_df = clean_df.join(pd.DataFrame.from_csv(filename, index_col=None), 
                                   lsuffix='_l' + str(n), rsuffix='_r' + str(n))
        os.remove(filename)
    
    return clean_df


# In[5]:

def write_online_table_to_file(url, datafile_name):
    page = urllib.urlopen(url).read()
    f = open(datafile_name, 'w')
    f.write(page)
    f.close()
    return datafile_name


##### Clean 2011 data

# In[19]:

write_online_table_to_file(tax_by_income_url[2011], "../data/raw_tax_data_2011.csv")
df11 = pd.DataFrame.from_csv("../data/raw_tax_data_2011.csv", index_col=None)
del df11["#"]
df11.to_csv('../data/cleaned_tax_data_2011.csv')


##### Clean 2010 data

# In[40]:

write_online_table_to_file(tax_by_income_url[2010], "../data/raw_tax_data_2010.csv")
rough_df = pd.DataFrame.from_csv("../data/raw_tax_data_2010.csv", index_col=None)


# In[41]:

header_lines = rough_df.query("code2 == '1'").index
df10 = clean_the_df(rough_df, header_lines)
df10['Item'] = df10['item_e_r1']
df10 = delete_extra_cols(df10)
df10.to_csv('../data/cleaned_tax_data_2010.csv')


##### Clean 2009 data

# In[35]:

write_online_table_to_file(tax_by_income_url[2009], "../data/raw_tax_data_2009.csv")
rough_df = pd.DataFrame.from_csv("../data/raw_tax_data_2009.csv", index_col=None)


# In[36]:

header_lines = rough_df.query("CODE2 == '1'").index
df09 = clean_the_df(rough_df, header_lines)
df09['Item'] = df09['iteme_r1']
df09 = delete_extra_cols(df09)
df09.to_csv('../data/cleaned_tax_data_2009.csv')


##### Clean 2008 data

# In[38]:

write_online_table_to_file(tax_by_income_url[2008], "../data/raw_tax_data_2008.csv")
rough_df = pd.DataFrame.from_csv("../data/raw_tax_data_2008.csv", index_col=None)


# In[39]:

header_lines = rough_df.query("CODE2 == '1'").index
df08 = clean_the_df(rough_df, header_lines)
df08['Item'] = df08['iteme_r1']
df08 = delete_extra_cols(df08)
df08.to_csv('../data/cleaned_tax_data_2008.csv')


### Compiling the datasets

# In[32]:

