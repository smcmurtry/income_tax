
# coding: utf-8

## Cleaning Income Tax Data

# In[1]:

import pandas as pd
import urllib
import os


# In[2]:

tax_by_income_url = {2008: "http://www.cra-arc.gc.ca/gncy/stts/gb08/pst/fnl/csv/table2-eng.csv",
                     2009: "http://www.cra-arc.gc.ca/gncy/stts/gb09/pst/fnl/csv/t02ca.csv",
                     2010: "http://www.cra-arc.gc.ca/gncy/stts/gb10/pst/fnl/csv/t02ca.csv",
                     2011: "http://www.cra-arc.gc.ca/gncy/stts/gb11/pst/fnl/csv/t02ca.csv",
                     2012: "http://www.cra-arc.gc.ca/gncy/stts/prlmnry/2012/tbl2-eng.csv"} # preliminary


### Preliminary cleaning

# In[3]:

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


# In[4]:

def write_online_table_to_file(url, datafile_name):
    page = urllib.urlopen(url).read()
    f = open(datafile_name, 'w')
    f.write(page)
    f.close()
    return datafile_name


### Save the online tables to files

##### 2012 data (preliminary)

# In[5]:

write_online_table_to_file(tax_by_income_url[2012], "../data/raw_tax_data_2012.csv")
df12 = pd.DataFrame.from_csv("../data/raw_tax_data_2012.csv", index_col=None)
df12.to_csv('../data/cleaned_tax_data_2012.csv')


##### 2011 data

# In[6]:

write_online_table_to_file(tax_by_income_url[2011], "../data/raw_tax_data_2011.csv")
df11 = pd.DataFrame.from_csv("../data/raw_tax_data_2011.csv", index_col=None)
df11.to_csv('../data/cleaned_tax_data_2011.csv')


##### 2010 data

# In[7]:

write_online_table_to_file(tax_by_income_url[2010], "../data/raw_tax_data_2010.csv")
rough_df = pd.DataFrame.from_csv("../data/raw_tax_data_2010.csv", index_col=None)


# In[8]:

header_lines = rough_df.query("code2 == '1'").index
df10 = clean_the_df(rough_df, header_lines)
df10['Item'] = df10['item_e_r1']
df10 = delete_extra_cols(df10)
df10.to_csv('../data/cleaned_tax_data_2010.csv')


##### 2009 data

# In[9]:

write_online_table_to_file(tax_by_income_url[2009], "../data/raw_tax_data_2009.csv")
rough_df = pd.DataFrame.from_csv("../data/raw_tax_data_2009.csv", index_col=None)


# In[10]:

header_lines = rough_df.query("CODE2 == '1'").index
df09 = clean_the_df(rough_df, header_lines)
df09['Item'] = df09['iteme_r1']
df09 = delete_extra_cols(df09)
df09.to_csv('../data/cleaned_tax_data_2009.csv')


##### 2008 data

# In[11]:

write_online_table_to_file(tax_by_income_url[2008], "../data/raw_tax_data_2008.csv")
rough_df = pd.DataFrame.from_csv("../data/raw_tax_data_2008.csv", index_col=None)


# In[12]:

header_lines = rough_df.query("CODE2 == '1'").index
df08 = clean_the_df(rough_df, header_lines)
df08['Item'] = df08['iteme_r1']
df08 = delete_extra_cols(df08)
df08.to_csv('../data/cleaned_tax_data_2008.csv')


# I may come back to this but it looks like the 2008 data is in a different format.

### Load the saved tables from files

# In[13]:

df09 = pd.DataFrame.from_csv('../data/cleaned_tax_data_2009.csv')
df10 = pd.DataFrame.from_csv('../data/cleaned_tax_data_2010.csv')
df11 = pd.DataFrame.from_csv('../data/cleaned_tax_data_2011.csv')
df12 = pd.DataFrame.from_csv('../data/cleaned_tax_data_2012.csv')


### Standardize the column names

# In[14]:

df12.columns


# In[15]:

for c in df11.columns:
    if c not in df12.columns: print c


# In[16]:

for c in df12.columns:
    if c not in df11.columns: print c


# In[17]:

df11.columns


# In[18]:

def clean_2011_2012_dfs(df):
    df["total #"] = df[' Grand total/Total global #']
    df["total $"] = df['Grand total/Total global $ (000)']
    df["<4999 #"] = df['4999 and under/Moins de 4 999 #']
    df["<4999 $"] = df['4999 and under/Moins de 4 999 $ (000)']
    df['>250000 #'] = df['250000 and over/et plus #']
    df['>250000 $'] = df['250000 and over/et plus $ (000)']
    return df


# In[20]:

df11 = clean_2011_2012_dfs(df11)
df12 = clean_2011_2012_dfs(df12)


# In[21]:

df10.columns


# In[22]:

df10['total #'] = df10['Grand total/Total global #']
df10['total $'] = df10['Grand total/Total global $']
df10['<4999 #'] = df10[df10.columns[2]] + df10['1 - 4999 #']
df10['<4999 $'] = df10[df10.columns[3]] + df10['1 - 4999 $']
df10['>250000 #'] = df10['250000 and over/et plus #']
df10['>250000 $'] = df10['250000 and over/et plus $']


# In[23]:

df09.columns


# In[24]:

df09['35000 - 39999 $'] = df09['35000 - 39999 $40000 - 44999 #']
df09['10000 - 14999 #'] = df09['10000 - 14999 # ']
df09['total #'] = df09['Grand total #/Total global #']
df09['total $'] = df09['Grand total $/Total global $']
df09['<4999 #'] = df09[df09.columns[2]] + df09['1 - 4999 #']
df09['<4999 $'] = df09[df09.columns[3]] + df09['1 - 4999 $']
df09['>250000 #'] = df09['250000 and over #/250 000 et plus #']
df09['>250000 $'] = df09['250000 and over $/250 000 et plus $']


# Create a tax year column so we can combine into a single table

# In[25]:

df12["tax_year"] = pd.Series([2012]*len(df12), index=df12.index)
df11["tax_year"] = pd.Series([2011]*len(df11), index=df11.index)
df10["tax_year"] = pd.Series([2010]*len(df10), index=df10.index)
df09["tax_year"] = pd.Series([2009]*len(df09), index=df09.index)


# After examining the datafiles, it appears that the dollar columns in all files are in thousands, even though the 2011 file is the only one that says this explicitly. I will remove the ' (000)' from the column titles for the 2011 file, and modify the dollar amounts later.

# In[26]:

def remove_thousands(df):
    for c in df.columns:
        if c.find('$') != -1:
            df[c[:-6]] = df[c]
    return df


# In[27]:

df11 = remove_thousands(df11)
df12 = remove_thousands(df12)


# In[28]:

common_cols = set(df12.columns).intersection(set(df11.columns)).intersection(set(df10.columns)).intersection(set(df09.columns))


# In[29]:

common_cols


# In[30]:

clean_cols = []
clean_cols.append('item')
clean_cols.append('type')
clean_cols.append('tax_year')
for c in common_cols:
    if '#' in c: clean_cols.append(c[:-2])


# In[31]:

half_n_rows = len(df12) + len(df11) + len(df10) + len(df09)


# In[32]:

df_master = pd.DataFrame(columns=clean_cols, index=range(2*half_n_rows))


# In[33]:

for c in df_master.columns:
    if c == 'item':
        df_master['item'] = (list(df12['Item']) + list(df11['Item']) + list(df10['Item']) + list(df09['Item']))*2
    elif c == 'type':
        df_master['type'] = ['#']*half_n_rows + ['$']*half_n_rows
    elif c == 'tax_year':
        df_master['tax_year'] = (list(df12['tax_year']) + list(df11['tax_year']) + list(df10['tax_year']) + list(df09['tax_year']))*2
    else:
        df_master[c] = list(df12[c + ' #']) + list(df11[c + ' #']) + list(df10[c + ' #']) + list(df09[c + ' #'])         + list(df12[c + ' $']) + list(df11[c + ' $']) + list(df10[c + ' $']) + list(df09[c + ' $'])


# In[34]:

df_master.head()


### Standardize the item titles

# In[47]:

len(set(df_master['item']))


# In[36]:

items_to_change = {"Universal Child Care Benefit (UCCB)": 'Universal Child Care Benefit',
                   'Social Benefits repayment': 'Social benefits repayment',
                   'Registered disability savings plan income (RDSP)': 'Registered disability savings plan income',
                   'Registered disability savings plan (RDSP) income': 'Registered disability savings plan income',
                   'Saskatchewan Pension Plan (SPP) deduction': 'Saskatchewan Pension Plan deduction',
                   'Registered pension plan (RPP) contributions': 'Registered pension plan contributions',
                   'Registered pension plan contributions (RPP)': 'Registered pension plan contributions',
                   'Registered Retirement Savings Plan (RRSP) income': 'Registered Retirement Savings Plan income',
                   'Investment Tax Credit': 'Investment tax credit',
                   'Employment\xa0 Insurance premiums payable on self-employment and other eligible': 'Employment Insurance premiums payable on self-employment',
                   'Employment Insurance premiums on self-employment and other eligible earnings': 'Employment Insurance premiums payable on self-employment',
                   'Net provincial tax': 'Net provincial or territorial tax',
                   'Old Age Security pension (OASP)': 'Old Age Security pension',
                   'Disability amount transferred from a dependent': 'Disability amount transferred from a dependant',
                   'Amount for infirm dependents age 18 or older': 'Amount for infirm dependants age 18 or older',
                   'Amounts transferred from spouse': 'Amounts transferred from spouse or common-law partner',
                   'Deductions for CPP/QPP contributions on self-employment and other earnings': 'Deductions for CPP or QPP contributions on self-employment and other earnings',
                   'Deductions for CPP/QPP contributions on self-employment/other earnings': 'Deductions for CPP or QPP contributions on self-employment and other earnings',
                   'CPP or QPP contributions on self-employment and other earnings' : 'CPP or QPP contributions self-employment',
                   'CPP or QPP contributions self-employment and other eligible earnings' : 'CPP or QPP contributions self-employment',
                   'Eligible cultural, ecological gifts': 'Eligible cultural and ecological gifts',
                   'Federal Political contribution tax credit': 'Federal political contribution tax credit',
                   'Federal political contribution tax  credit': 'Federal political contribution tax credit',
                   'CPP or QPP contributions employment': 'CPP or QPP contributions through employment',
                   'Net partnership income (Limited or non-active partners only)': 'Net partnership income',
                   'Registered retirement savings plan income (RRSP)': 'Registered Retirement Savings Plan income'}


# In[37]:

for i in df_master.index:
    if df_master.item[i] in items_to_change.keys():
        df_master.ix[i, 'item'] = items_to_change[df_master.item[i]]


### Making the column headings more readable

# In[38]:

for c in df_master.columns: print c


# In[40]:

col_labels = {
"<4999": "< $5k",
"5000 - 9999": "$5k - 10k",
"10000 - 14999": "$10k - 15k",
"15000 - 19999": "$15k - 20k",
"20000 - 24999": "$20k - 25k",
"25000 - 29999": "$25k - 30k",
"30000 - 34999": "$30k - 35k",
"35000 - 39999": "$35k - 40k",
"40000 - 44999": "$40k - 45k",
"45000 - 49999": "$45k - 50k",
"50000 - 54999": "$50k - 55k",
"55000 - 59999": "$55k - 60k",
"60000 - 69999": "$60k - 70k",
"70000 - 79999": "$70k - 80k",
"80000 - 89999": "$80k - 90k",
"90000 - 99999": "$90k - 100k",
"100000 - 149999": "$100k - 150k",
"150000 - 249999": "$150k - 250k",
">250000": "> $250k"}


# In[41]:

for col in df_master.columns:
    if col in col_labels:
        df_master[col_labels[col]] = df_master[col]
        del df_master[col]


# In[42]:

ordered_cols = ['item', 'type', 'tax_year', 'total', 
                '< $5k', '$5k - 10k', '$10k - 15k', 
                '$15k - 20k', '$20k - 25k', '$25k - 30k',
                '$30k - 35k', '$35k - 40k', '$40k - 45k',
                '$45k - 50k', '$50k - 55k', '$55k - 60k',
                '$60k - 70k', '$70k - 80k', '$80k - 90k',
                '$90k - 100k', '$100k - 150k', '$150k - 250k', 
                '> $250k']


# In[43]:

df_master = df_master[ordered_cols]


# In[44]:

df_master.query("type == '$'").head()


### Multiply the dollar amounts by 1000

# In[45]:

for i in df_master.index:
    print i,
    if df_master.type[i] == '$':
        for col in set(df_master.columns).difference(set(['item', 'type', 'tax_year'])):
            # all the dollar amounts are already integers, so I will keep them that way
            df_master.ix[i, col] = 1000 * df_master[col][i]


### Save the cleaned data

# In[46]:

df_master.to_csv('../data/all_clean_tax_data_2.csv')


# In[29]:

