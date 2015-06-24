
# coding: utf-8

#### Tax Data by Income

# I just found a better link to the income data I was telling you about:
# http://www.cra-arc.gc.ca/gncy/stts/t1fnl-eng.html
#  
# <p>you can click on one of the three available years and then get the data in PDF or CSV (we had a poor intern clean up a machine converted version of the pdf). "Final Table 2 - All returns by total income class" is the one I think most interesting.
#  
# <p>there are a bunch of other tax filing related datasets available here: http://www.cra-arc.gc.ca/gncy/stts/menu-eng.html including 'T1 preliminary statistics' which are similar to the first link but run from 2006 to 2012.

# In[3]:

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
get_ipython().magic(u'matplotlib inline')
# import sys
# sys.path.append('/Users/stephenmcmurtry/work/python_libraries')
import useful as us
from matplotlib.ticker import FuncFormatter


##### Data handling for plotting functions

# In[2]:

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

def bar_plot(values, labels, title, xformatter=None):
    f, ax = plt.subplots(1, 1, figsize=(8, 8))
    ax.barh(range(len(values)), values, align='center', color='grey', edgecolor='grey');
    ax.set_ylim([-1, len(values)])
    ax.set_yticks(range(len(values)))
    ax.set_yticklabels(labels)
    ax.vlines(ax.get_xticks(), ax.get_ybound()[0], ax.get_ybound()[1], color='white', linewidth=2)
    if xformatter: ax.xaxis.set_major_formatter(xformatter)
    ax.set_title(title)
    return f, ax


# In[11]:

unit_figuring = {'$':{'$':'%', '-':'$'},
                 '-':{'$':'1/$', '-':'-'}}

def by_income_bin(df, item_name, col_list): 
    return [int(df.query("Item == @item_name")[col]) for col in col_list]

def plot_item(df, item_name, divisor_fn=None, col_type='dollar'):
    
    dollar_cols = [c for c in df.columns if c.find('$') != -1]
    number_cols = [c for c in df.columns if c.find('#') != -1]
    number_of_returns_by_income = by_income_bin(df, 'Total number of returns', number_cols)
    dollars_of_income_by_income = np.multiply(1000., by_income_bin(df, 'Total income assessed', dollar_cols))
    
    if col_type == 'dollar':
        col_names = dollar_cols
    elif col_type == 'number':
        col_names = number_cols
    else:
        print 'wtf!'
        
    def per_return(y):
        y_per_return = np.divide([float(i) for i in y], [float(i) for i in number_of_returns_by_income])
        return y_per_return

    def per_dollar_income(y):
        y_per_dollar_income = np.divide([float(i) for i in y], [float(i) for i in dollars_of_income_by_income])
        return y_per_dollar_income
    
    if col_names == dollar_cols:
        numerator_unit = '$'
    elif col_names == number_cols:
        numerator_unit = '-'
    else:
        print 'wtf!'
        
    item_amount = by_income_bin(df, item_name, col_names)
    item_amount = np.multiply(1000., item_amount)
    if divisor_fn == "per_return":
        item_amount = per_return(item_amount)
        denomonator_unit = '-'
        xlabel_text = 'per return '
    elif divisor_fn == "per_dollar_income":
        item_amount = per_dollar_income(item_amount)
        denomonator_unit = '$'
        xlabel_text = 'per dollar of income '
    else:
        denomonator_unit = '-'
        xlabel_text = ''
    final_unit = unit_figuring[numerator_unit][denomonator_unit]
    
    mpl_formatters = {'$':mpl_dollar_formatter, '-':mpl_number_formatter, 
                      '%':mpl_percent_formatter}
    
    item_amount_plot = item_amount[1:-1]
    labels = col_names[1:-1]
    labels = [w[:-8] for w in labels]
    f, ax = bar_plot(item_amount_plot, labels, '', xformatter=mpl_formatters[final_unit])
    ax.set_xlabel(item_name + ' ' + xlabel_text + "\n")
    ax.xaxis.set_label_position('top')
    ax.xaxis.set_ticks_position('top')
    us.remove_border(ax, top_ax=True, top_tick=True)
    
    return f, ax


##### Loading the data

# In[12]:

df = pd.DataFrame.from_csv('../data/cleaned_tax_data_2011.csv')


# In[21]:

f, ax = plot_item(df, 'Total tax payable', divisor_fn="per_dollar_income")


##### Task: Make a bar graph that shows the number of tax returns in each income bin

# In[15]:

f, ax = plot_item(df, 'Total income assessed')


# In[16]:

f, ax = plot_item(df, 'Total number of returns', col_type='number')


##### Task: Plot the tax income for each income bin

# In[18]:

f, ax = plot_item(df, 'Total tax payable', divisor_fn="per_return")


##### More exploration

# In[190]:

f, ax = plot_item(df, "Children's fitness amount", dollar_cols, divisor_fn=per_return)
f.savefig('childrens_fitness_by_income.png', bbox_inches='tight')


# In[192]:

f, ax = plot_item(df, "Children's arts amount", dollar_cols, divisor_fn=per_return)


# In[193]:

f, ax = plot_item(df, "Net federal tax", dollar_cols, divisor_fn=per_return)


# In[194]:

f, ax = plot_item(df, "Net Provincial Tax", dollar_cols, divisor_fn=per_return)


# In[202]:

f, ax = plot_item(df, 'RRSP deduction', dollar_cols, divisor_fn=per_return)


# In[19]:

f, ax = plot_item(df, 'Interest and other investment income', divisor_fn="per_return")
#f.savefig('investment_income_by_income.png', bbox_inches='tight')


# In[196]:

f, ax = plot_item(df, 'Employment income', dollar_cols, divisor_fn=per_return)


# In[197]:

f, ax = plot_item(df, 'Net income after adjustments', dollar_cols, divisor_fn=per_return)


# In[199]:

f, ax = plot_item(df, 'Carrying charges and interest expenses', dollar_cols, divisor_fn=per_return)


# In[201]:

f, ax = plot_item(df, 'Interest paid on student loans', dollar_cols, divisor_fn=per_return)


# In[4]:

