
# coding: utf-8

## Cleaning Income Tax Data

# In[1]:

import pandas as pd
import urllib
import os


# 2004 to 2008 statistics were based on a stratified random sample of individual income tax and benefit returns. However, beginning with the 2009 tax year, Final Statistics contains data based on all of the returns filed. The most recent assessment is used in the compilation of the statistics.

# In[10]:

tax_by_income_url = {2004: "http://www.cra-arc.gc.ca/gncy/stts/gb04/pst/fnl/csv/table2.csv",
                     2005: "http://www.cra-arc.gc.ca/gncy/stts/gb05/pst/fnl/csv/table2.csv",
                     2006: "http://www.cra-arc.gc.ca/gncy/stts/gb06/pst/fnl/csv/t02ca.csv",
                     2007: "http://www.cra-arc.gc.ca/gncy/stts/gb07/pst/fnl/csv/t02ca.csv",
                     2008: "http://www.cra-arc.gc.ca/gncy/stts/gb08/pst/fnl/csv/t02ca.csv",
                     2009: "http://www.cra-arc.gc.ca/gncy/stts/gb09/pst/fnl/csv/t02ca.csv",
                     2010: "http://www.cra-arc.gc.ca/gncy/stts/gb10/pst/fnl/csv/t02ca.csv",
                     2011: "http://www.cra-arc.gc.ca/gncy/stts/gb11/pst/fnl/csv/t02ca.csv",
                     2012: "http://www.cra-arc.gc.ca/gncy/stts/prlmnry/2012/tbl2-eng.csv"} # preliminary data

column_dictionary_04_08 = 'http://www.cra-arc.gc.ca/gncy/stts/gb04/pst/fnl/tb2_f1-f7-eng.html'


### Preliminary cleaning

# In[11]:

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


# In[12]:

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


##### 2004 - 2008 data

# In[16]:

def save_rough_files(year):
    filename = "../data/raw_tax_data_" + str(year) + ".csv"
    write_online_table_to_file(tax_by_income_url[year], filename)
    return filename


# In[17]:

f_names = {}
for year in [2004, 2005, 2006, 2007, 2008]:
    f_names[year] = save_rough_files(year)


# In[19]:

dfd = {}
for year in f_names:
    dfd[year] = pd.DataFrame.from_csv(f_names[year], index_col=None)


# In[22]:

dfd[2004].columns


##### Get a dictionary for the columns

# In[146]:

import col_dict_2004_08


# In[137]:

col_dict = {}
for row in col_dict_2004_08.col_dict:
    f7_val = row[0]
    for i, x in enumerate(row[1:]):
        f_col = col_dict_2004_08.list_order[i+1]
        col_dict[(f7_val, f_col)] = x


# In[138]:

def flatten_df(stacked_df):
    data_cols = ['F1','F2','F3','F4','F5','F6']
    df = pd.DataFrame(index=range(len(set(stacked_df['CODE2']))))
    df['tax_year'] = pd.Series(index=df.index)
    for i in stacked_df.index:
        f7_val = stacked_df['f7'][i]
        item_num = stacked_df['CODE2'][i]
        tax_year = stacked_df['taxyr'][i]
        df.ix[item_num-1, 'tax_year'] = tax_year
        for c in data_cols:
            d = stacked_df[c][i]
            key = (str(f7_val), c.lower())
            if key == ('8', 'f5'): break
            new_col = col_dict[key]
            new_col = new_col.replace('$', '')
            if new_col not in df.columns: df[new_col] = pd.Series(index=df.index)
            df.ix[item_num-1, new_col] = d
    return df


# In[139]:

flat_df = {}
for year in dfd: flat_df[year] = flatten_df(dfd[year])


# In[140]:

def get_item_dict(df):
    item_dict = {}
    for i in df.index:
        item_dict[df['CODE2'][i]] = df['ITEME'][i]
    return item_dict


# In[141]:

item_dict = {}
for year in [2005, 2006, 2007, 2008]:
    item_dict[year] = get_item_dict(dfd[year])


# I semi-manually assembled this dictionary from an html table: http://www.cra-arc.gc.ca/gncy/stts/gb04/pst/fnl/tb2-5-eng.html

# In[142]:

import item_dict_2004
item_dict[2004] = {}
for pair in item_dict_2004.item_dict:
    item_dict[2004][pair[1]] = pair[0]


# In[143]:

for year in flat_df:
    flat_df[year]['item'] = pd.Series(index=flat_df[year].index)
    for i in flat_df[year].index:
        flat_df[year].ix[i, 'item'] = item_dict[year][i+1]


# In[147]:

dfo = pd.concat([flat_df[year] for year in flat_df], ignore_index=True)


# In[149]:

dfo.to_csv("../data/partially_clean_04_08.csv")


# In[201]:

dfo = pd.DataFrame.from_csv("../data/partially_clean_04_08.csv")


### Load the saved tables from files

# In[50]:

df09 = pd.DataFrame.from_csv('../data/cleaned_tax_data_2009.csv')
df10 = pd.DataFrame.from_csv('../data/cleaned_tax_data_2010.csv')
df11 = pd.DataFrame.from_csv('../data/cleaned_tax_data_2011.csv')
df12 = pd.DataFrame.from_csv('../data/cleaned_tax_data_2012.csv')


### Standardize the column names

# In[51]:

df12.columns


# In[52]:

for c in df11.columns:
    if c not in df12.columns: print c


# In[53]:

for c in df12.columns:
    if c not in df11.columns: print c


# In[54]:

df11.columns


# In[55]:

def clean_2011_2012_dfs(df):
    df["total #"] = df[' Grand total/Total global #']
    df["total $"] = df['Grand total/Total global $ (000)']
    df["<4999 #"] = df['4999 and under/Moins de 4 999 #']
    df["<4999 $"] = df['4999 and under/Moins de 4 999 $ (000)']
    df['>250000 #'] = df['250000 and over/et plus #']
    df['>250000 $'] = df['250000 and over/et plus $ (000)']
    return df


# In[56]:

df11 = clean_2011_2012_dfs(df11)
df12 = clean_2011_2012_dfs(df12)


# In[57]:

df10.columns


# In[58]:

df10['total #'] = df10['Grand total/Total global #']
df10['total $'] = df10['Grand total/Total global $']
df10['<4999 #'] = df10[df10.columns[2]] + df10['1 - 4999 #']
df10['<4999 $'] = df10[df10.columns[3]] + df10['1 - 4999 $']
df10['>250000 #'] = df10['250000 and over/et plus #']
df10['>250000 $'] = df10['250000 and over/et plus $']


# In[59]:

df09.columns


# In[60]:

df09['35000 - 39999 $'] = df09['35000 - 39999 $40000 - 44999 #']
df09['10000 - 14999 #'] = df09['10000 - 14999 # ']
df09['total #'] = df09['Grand total #/Total global #']
df09['total $'] = df09['Grand total $/Total global $']
df09['<4999 #'] = df09[df09.columns[2]] + df09['1 - 4999 #']
df09['<4999 $'] = df09[df09.columns[3]] + df09['1 - 4999 $']
df09['>250000 #'] = df09['250000 and over #/250 000 et plus #']
df09['>250000 $'] = df09['250000 and over $/250 000 et plus $']


# In[205]:

dfo.columns


# In[203]:

del dfo['50,000 and over (number)']
del dfo['50,000 and over(amount)']
del dfo['50,000 - 100,000 (number)']
del dfo['50,000 - 100,000 (amount)']
del dfo['Grand Total (number)']
del dfo['Grand total (amount)']
del dfo['30,000 - 40,000 (number)']
del dfo['30,000 - 40,000 (amount)']
del dfo['40,000 - 50,000 (number)']
del dfo['40,000 - 50,000 (amount)']


# In[204]:

for c in dfo.columns:
    c2 = c.replace('Loss and nil(amount)', 'Loss and nil (amount)')
    c2 = c2.replace('250,000 and over', '>250,000')
    c2 = c2.replace('(amount)', '$')
    c2 = c2.replace('(number)', '#')
    c2 = c2.replace(',', '')
    c2 = c2.replace('Loss and nil', '<0')
    dfo[c2] = dfo[c]
    if c != c2: del dfo[c]


# Create a tax year column so we can combine into a single table

# In[61]:

df12["tax_year"] = pd.Series([2012]*len(df12), index=df12.index)
df11["tax_year"] = pd.Series([2011]*len(df11), index=df11.index)
df10["tax_year"] = pd.Series([2010]*len(df10), index=df10.index)
df09["tax_year"] = pd.Series([2009]*len(df09), index=df09.index)


# After examining the datafiles, it appears that the dollar columns in all files are in thousands, even though the 2011 file is the only one that says this explicitly. I will remove the ' (000)' from the column titles for the 2011 file, and modify the dollar amounts later.

# In[62]:

def remove_thousands(df):
    for c in df.columns:
        if c.find('$') != -1:
            df[c[:-6]] = df[c]
    return df


# In[63]:

df11 = remove_thousands(df11)
df12 = remove_thousands(df12)


# In[64]:

common_cols = set(df12.columns).intersection(set(df11.columns)).intersection(set(df10.columns)).intersection(set(df09.columns))


# In[66]:

clean_cols = []
clean_cols.append('item')
clean_cols.append('type')
clean_cols.append('tax_year')
for c in common_cols:
    if '#' in c: clean_cols.append(c[:-2])


# In[67]:

half_n_rows = len(df12) + len(df11) + len(df10) + len(df09)


# In[68]:

df_master = pd.DataFrame(columns=clean_cols, index=range(2*half_n_rows))


# In[69]:

for c in df_master.columns:
    if c == 'item':
        df_master['item'] = (list(df12['Item']) + list(df11['Item']) + list(df10['Item']) + list(df09['Item']))*2
    elif c == 'type':
        df_master['type'] = ['#']*half_n_rows + ['$']*half_n_rows
    elif c == 'tax_year':
        df_master['tax_year'] = (list(df12['tax_year']) + list(df11['tax_year']) + list(df10['tax_year']) + list(df09['tax_year']))*2
    else:
        df_master[c] = list(df12[c + ' #']) + list(df11[c + ' #']) + list(df10[c + ' #']) + list(df09[c + ' #'])         + list(df12[c + ' $']) + list(df11[c + ' $']) + list(df10[c + ' $']) + list(df09[c + ' $'])


# Now for 2004 - 2008

# In[213]:

new_cols = ['item', 'type', 'tax_year']
for c in dfo.columns:
    if '#' in c: new_cols.append(c[:-2])


# In[214]:

dfo2 = pd.DataFrame(columns=new_cols, index=range(2*len(dfo)))


# In[215]:

for c in dfo2.columns:
    if c == 'item':
        dfo2[c] = list(dfo[c]) * 2
    elif c == 'tax_year':
        dfo2[c] = [int(x) for x in list(dfo[c])] * 2
    elif c == 'type':
        dfo2[c] = ['#']*len(dfo) + ['$']*len(dfo)
    else:
        dfo2[c] = list(dfo[c + ' #']) + list(dfo[c + ' $'])


### Making the column headings more readable

# In[219]:

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

col_labels_04_08 = {
'<0': '< $0',
"1 - 10000": "$1 - 10k",
"10000 - 15000": "$10k - 15k",
"15000 - 20000": "$15k - 20k",
"20000 - 25000": "$20k - 25k",
"25000 - 30000": "$25k - 30k",
"30000 - 35000": "$30k - 35k",
"35000 - 40000": "$35k - 40k",
"40000 - 45000": "$40k - 45k",
"45000 - 50000": "$45k - 50k",
"50000 - 60000": "$50k - 60k",
"60000 - 70000": "$60k - 70k",
"70000 - 80000": "$70k - 80k",
"80000 - 90000": "$80k - 90k",
"90000 - 100000": "$90k - 100k",
"100000 - 150000": "$100k - 150k",
"150000 - 250000": "$150k - 250k",
">250000": "> $250k"}


# In[220]:

def rename_cols(df, col_label_dict):
    for col in df.columns:
        if col in col_label_dict:
            df[col_label_dict[col]] = df[col]
            del df[col]
    return df


# In[221]:

df_master = rename_cols(df_master, col_labels)
dfo2 = rename_cols(dfo2, col_labels_04_08)


# In[81]:

ordered_cols = ['item', 'type', 'tax_year', 'total', 
                '< $5k', '$5k - 10k', '$10k - 15k', 
                '$15k - 20k', '$20k - 25k', '$25k - 30k',
                '$30k - 35k', '$35k - 40k', '$40k - 45k',
                '$45k - 50k', '$50k - 55k', '$55k - 60k',
                '$60k - 70k', '$70k - 80k', '$80k - 90k',
                '$90k - 100k', '$100k - 150k', '$150k - 250k', 
                '> $250k']


# In[82]:

df_master = df_master[ordered_cols]


### Multiply the dollar amounts by 1000

# In[222]:

def dollars_times_thous(df):
    for i in df.index:
        print i,
        if df.type[i] == '$':
            for col in set(df.columns).difference(set(['item', 'type', 'tax_year'])):
                # all the dollar amounts are already integers, so I will keep them that way
                df.ix[i, col] = 1000 * df[col][i]
    return df


# In[223]:

df_master = dollars_times_thous(df_master)
dfo2 = dollars_times_thous(dfo2)


### Save the cleaned data

# In[85]:

df_master.to_csv('../data/tax_data_unclean_items.csv')
dfo2.to_csv('../data/tax_data_unclean_items_04_08.csv')


### Standardize the item titles

# In[3]:

import pandas as pd
df_master = pd.DataFrame.from_csv('../data/tax_data_unclean_items.csv')
dfo2 = pd.DataFrame.from_csv('../data/tax_data_unclean_items_04_08.csv')


# In[4]:

print len(set(df_master['item']))
print len(set(dfo2['item']))


# In[5]:

set(list(dfo2['item'])).difference(set(synonym_dict.keys()))


# In[235]:

for x in all_items: print x


# In[7]:

import item_synonyms_2


# In[8]:

item_synonyms_2.synonyms


# In[10]:

synonym_dict = {}
for li in item_synonyms_2.synonyms:
    if len(li) > 1:
        for item in li:
            synonym_dict[item] = li[0]


# In[11]:

synonym_dict


# In[13]:

def clean_item_names(df, synonym_dict):
    for i in df.index:
        if df.item[i] in synonym_dict.keys():
            df.ix[i, 'item'] = synonym_dict[df.item[i]]
    return df


# In[14]:

df_master = clean_item_names(df_master, synonym_dict)
dfo2 = clean_item_names(dfo2, synonym_dict)


# In[15]:

dfo2.to_csv('../data/all_clean_tax_data_04_08.csv')
df_master.to_csv('../data/all_clean_tax_data.csv')


#### Converting to JSON

# In[16]:

def write_df_to_json(df, open_file, last_write=True):
    for i in df.index:
        row_str = '{'
        for j, c in enumerate(df.columns):
            row_str += '"' + c + '"' + ': ' + '"' + str(df[c][i]) 
            if j+1 == len(df.columns): row_str += '"'
            else: row_str += '", '
        if i+1 == len(df) and last_write: row_str += '}\n'
        else: row_str += '},\n'
        open_file.write(row_str)


# In[17]:

f = open('../data/data_2.json', 'w')
f.write('[')
write_df_to_json(df_master, f, last_write=False)
write_df_to_json(dfo2, f, last_write=True)
f.write(']')
f.close()


# In[ ]:

