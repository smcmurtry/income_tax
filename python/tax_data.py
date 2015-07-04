
# coding: utf-8

#### Tax Data by Income

# From Tim:
# 
# I just found a better link to the income data I was telling you about:
# http://www.cra-arc.gc.ca/gncy/stts/t1fnl-eng.html
#  
# <p>you can click on one of the three available years and then get the data in PDF or CSV (we had a poor intern clean up a machine converted version of the pdf). "Final Table 2 - All returns by total income class" is the one I think most interesting.
#  
# <p>there are a bunch of other tax filing related datasets available here: http://www.cra-arc.gc.ca/gncy/stts/menu-eng.html including 'T1 preliminary statistics' which are similar to the first link but run from 2006 to 2012.

# I may want to switch to the preliminary files and try to convert those: http://www.cra-arc.gc.ca/gncy/stts/ntrm-eng.html
# 
# And here is a description of all the line items: http://www.cra-arc.gc.ca/gncy/stts/gb11/pst/fnl/dsctm-eng.html

# In[2]:

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
get_ipython().magic(u'matplotlib inline')
import useful as us
from matplotlib.ticker import FuncFormatter


##### Data handling for plotting functions

# In[3]:

def number_formatter(n):
    "Find the correct suffix, divide the original number, and return the new number + suffix"
    if 0 <= n < 1E3: 
        suffix = ' '
    elif 1E3 <= n < 1E6:
        suffix = 'k'
    elif 1E6 <= n < 1E9:
        suffix = 'M'
    elif 1E9 <= n < 1E12:
        suffix = 'B'
    elif 1E12 <= n < 1E15:
        suffix = 'T'
    else:
        suffix = 'really big!'
    
    order = {' ':1., 'k':1E3, 'M':1E6, 'B':1E9, 'T':1E12, 'really big!':1.}
    suffix2print = {' ':'', 'k':'k', 'M':'M', 'B':'B', 'T':'T', 'really big!':'really big!'}
    smaller_n = n / order[suffix]
    
    if smaller_n%1 < 0.0001: 
        return str(int(smaller_n)) + suffix2print[suffix]
    else: 
        return str(smaller_n) + suffix2print[suffix]
    
def _mpl_dollar_formatter(y, position): return '$' + number_formatter(y)

def _mpl_number_formatter(y, position): return number_formatter(y)

def _mpl_percent_formatter(y, position): return number_formatter(100 * y) + '%'
    
mpl_number_formatter = FuncFormatter(_mpl_number_formatter)
mpl_dollar_formatter = FuncFormatter(_mpl_dollar_formatter)
mpl_percent_formatter = FuncFormatter(_mpl_percent_formatter)

def bar_plot(values, title, labels=[], xformatter=None):
    f, ax = plt.subplots(1, 1, figsize=(8, 8))
    ax.barh(range(len(values)), values, align='center', color='grey', edgecolor='grey');
    ax.set_ylim([-1, len(values)])
    ax.set_yticks(range(len(values)))
    ax.set_yticklabels(labels)
    ax.vlines(ax.get_xticks(), ax.get_ybound()[0], ax.get_ybound()[1], color='white', linewidth=2)
    if xformatter: ax.xaxis.set_major_formatter(xformatter)
    ax.set_title(title)
    return f, ax


# In[4]:

unit_figuring = {'$': {'$': '%', '#': '$', '-': '$'},
                 '#': {'$': '1/$', '#': '#', '-':'#'}}

x_label_figuring = {'$': {'$': '(as % of income)', '#': '(per return)', '-': ''},
                 '#': {'$': '# of returns per dollar of income', '#': '# of returns per return', '-': ''}}

mpl_formatters = {'$':mpl_dollar_formatter, '#':mpl_number_formatter, 
                  '%':mpl_percent_formatter}

def vector_division(numerator, denomonator):
    result = np.divide([float(n) for n in numerator], [float(n) for n in denomonator])
    return result

def get_row_data_as_list(df, cols, item_name, item_unit, tax_year):
    row = df.query("item == @item_name and type == @item_unit and tax_year == @tax_year")
    row_data = [row[c][row.index[0]] for c in cols]
    return row_data

def plot_item(df, item_name='', item_unit='$', divisor='', tax_year=2009):
    
    income_cols = df.columns[4:] # excludes 'item', 'type', 'tax_year', 'total'
    numerator_data = get_row_data_as_list(df, income_cols, item_name, item_unit, tax_year)
    
    if divisor == "per_return":    
        denomonator_data = get_row_data_as_list(df, income_cols, 'Total number of returns', '#', tax_year)
        denomonator_unit = '#'
    elif divisor == "per_dollar_income":
        denomonator_data = get_row_data_as_list(df, income_cols, 'Total income assessed', '$', tax_year)
        denomonator_unit = '$'
    elif divisor == "avg_claim":
        denomonator_data = get_row_data_as_list(df, income_cols, item_name, '#', tax_year)
        denomonator_unit = '-'
    else:
        denomonator_data = np.ones_like(numerator_data)
        denomonator_unit = '-'
    
    plot_data = vector_division(numerator_data, denomonator_data)
    final_unit = unit_figuring[item_unit][denomonator_unit]
    
    f, ax = bar_plot(plot_data, '', labels=income_cols, xformatter=mpl_formatters[final_unit])
    ax.set_xlabel(item_name + ' ' + x_label_figuring[item_unit][denomonator_unit] + "\n")
    ax.xaxis.set_label_position('top')
    ax.xaxis.set_ticks_position('top')
    us.remove_border(ax, top_ax=True, top_tick=True)
    
    return f, ax


##### Loading the data

# In[5]:

df = pd.DataFrame.from_csv('../data/all_clean_tax_data.csv')


# In[6]:

df.head()


# In[7]:

set(df.item)


# In[14]:

f, ax = plot_item(df, item_name='Tuition, education, and textbook amounts transferred from a child')


# In[15]:

f, ax = plot_item(df, item_name='Tuition, education, and textbook amounts transferred from a child', item_unit='#')


# In[10]:

f, ax = plot_item(df, item_name='Tuition, education, and textbook amounts transferred from a child', divisor="per_return")


# In[11]:

f, ax = plot_item(df, item_name='Tuition, education, and textbook amounts transferred from a child', divisor="avg_claim")


# In[13]:

f, ax = plot_item(df, item_name='Tuition, education, and textbook amounts transferred from a child', item_unit='#',divisor="per_return")


# There are a few distinct types of plots we can make, all by income bucket:
# * total value of all claims
# * average value of each claim
# * average value of claim per return
# * average value per return as fraction of income (this may only make sense for seeing the average tax rate?)
# * total number of tax claims
# * fraction of returns with claim

# In[34]:

f, ax = plot_item(df, item_name='Total tax payable')


# In[28]:

f, ax = plot_item(df, item_name='Total tax payable', item_unit='$', divisor="per_dollar_income")


##### Task: Make a bar graph that shows the number of tax returns in each income bin

# In[29]:

f, ax = plot_item(df, item_name='Total income assessed', item_unit='$')


# In[30]:

f, ax = plot_item(df, item_name='Total number of returns', item_unit='#')


##### Task: Plot the tax income for each income bin

# In[33]:

f, ax = plot_item(df, 'Total tax payable', divisor="per_return")


##### More exploration

# In[36]:

f, ax = plot_item(df, item_name="Children's fitness amount", divisor="per_return")
#f.savefig('childrens_fitness_by_income.png', bbox_inches='tight')


# In[39]:

f, ax = plot_item(df, item_name="Children's arts amount", divisor="per_return", tax_year=2011)


# In[19]:

f, ax = plot_item(df, item_name="Net federal tax", divisor="per_dollar_income", tax_year=2011)


# In[20]:

f, ax = plot_item(df, item_name="Net federal tax", divisor="per_dollar_income", tax_year=2010)


# In[21]:

f, ax = plot_item(df, item_name="Net federal tax", divisor="per_dollar_income", tax_year=2009)


# In[42]:

f, ax = plot_item(df, item_name="Net Provincial Tax", divisor="per_return", tax_year=2011)


# In[45]:

f, ax = plot_item(df, item_name='RRSP deduction', divisor="per_return", tax_year=2011)


# In[46]:

f, ax = plot_item(df, item_name='Interest and other investment income', divisor="per_return")
#f.savefig('investment_income_by_income.png', bbox_inches='tight')


# In[47]:

f, ax = plot_item(df, item_name='Employment income', divisor="per_return")


# In[48]:

f, ax = plot_item(df, item_name='Net income after adjustments', divisor="per_return")


# In[49]:

f, ax = plot_item(df, item_name='Carrying charges and interest expenses', divisor="per_return")


# In[17]:

f, ax = plot_item(df, item_name='Interest paid on student loans', divisor="per_dollar_income")


# In[22]:

