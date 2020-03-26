#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 23 07:50:35 2020

@author: sarathy
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scipy.stats as stats


# age distribution
# age distribution
age_values = np.arange(0,81,1)
age_distribution_over_gap5 = [0.073, 0.078, 0.083, 0.086, 0.102, 0.11, 0.098, 0.081, 0.071, 0.059, 0.049, 0.037, 0.03, 0.021, 0.01, 0.007, 0.005]

age_distribution = []
for i in range(0,len(age_distribution_over_gap5)-1):
    for j in range(0,5):
        age_distribution.append(age_distribution_over_gap5[i]/5)
age_distribution.append(age_distribution_over_gap5[16])
age_distribution = np.array(age_distribution)
age_distribution = age_distribution/sum(age_distribution)

# household size distributin
household_sizes = [1,2,3,4,5,6]
household_distribution = [0.0417, 0.1308, 0.2228, 0.3077, 0.1530, 0.1439]
household_distribution = household_distribution/np.sum(household_distribution)
# generate s sample of size of workplace 
a=3.26
c=0.97
m_max=2870
    #function to generate a truncated Zipf sample

workplace_sizes = np.arange(m_max)
p_nplus = np.arange(float(m_max))
for m in range(m_max):
    p_nplus[m] =  ((( (1+m_max/a)/(1+m/a))**c) -1) / (((1+m_max/a)**c) -1)

p_nminus = 1.0 - p_nplus
p_n = np.arange(float(m_max))
prev=0.0
for m in range(1, m_max):
    p_n[m] = p_nminus[m] - prev
    prev = p_nminus[m] 

bzipf = stats.rv_discrete (name='bzipf', values=(workplace_sizes, p_n))


individuals = pd.read_json('./banglore_individuals.json')

age = {'id':np.unique(individuals['age'].values), 'number of people':[0 for i in range(0,len(np.unique(individuals['age'].values)))]}
age = pd.DataFrame(age)
x = np.unique(individuals['household'].values)
x = x[~np.isnan(x)]
households = {'id':x, 'number of people': [0 for i in range(0,len(x))] }
households = pd.DataFrame(households)

x = np.unique(individuals['school'].values)
x = x[~np.isnan(x)]
schools = {'id':x, 'number of people': [0 for i in range(0,len(x))] }
schools = pd.DataFrame(schools)

x = np.unique(individuals['workplace'].values)
x = x[~np.isnan(x)]

workplaces = {'id':x, 'number of people': [0 for i in range(0,len(x))] }
workplaces = pd.DataFrame(workplaces)

for i in range(0,len(individuals)):
    print(i/len(individuals))
    age.at[age['id']==individuals.loc[i,'age'],'number of people'] = 1+age.loc[age['id']==individuals.loc[i,'age'],'number of people']
    
    households.at[households['id']==individuals.loc[i,'household'],'number of people'] = 1+households.loc[households['id']==individuals.loc[i,'household'],'number of people']

    if not(np.isnan(individuals.loc[i,'school'])):
        schools.at[schools['id']==individuals.loc[i,'school'],'number of people'] = 1+schools.loc[schools['id']==individuals.loc[i,'school'],'number of people']
        
    if not(np.isnan(individuals.loc[i,'workplace'])):
        workplaces.at[workplaces['id']==individuals.loc[i,'workplace'],'number of people'] = 1+workplaces.loc[workplaces['id']==individuals.loc[i,'workplace'],'number of people']
    
# plot age distribution
plt.plot(age['number of people'].values/(np.sum(age['number of people'].values)), 'r')
plt.plot(age_distribution)
plt.xlabel('Age')
plt.ylabel('Density')
plt.title('Distribution of age')
plt.grid(True)
plt.xticks(np.arange(0,81,10), np.concatenate((age_values[np.arange(0,71,10)], ['80+'])) )
plt.savefig('age')
plt.show()

plt.close()

# plot household size distribution
#HH_ranges = ['1','2','3','4','5','6','7-10','11-14','15+']
HH_ranges = [1,2,3,4,5,6]
HH_numbers = np.array([len(households.loc[households['number of people']==HH_ranges[i]]) for i in range(0,len(HH_ranges))])
HH_output_distribution = HH_numbers/sum(HH_numbers)
plt.plot(HH_ranges,household_distribution)
plt.plot(HH_ranges,HH_output_distribution,'r')
plt.xticks(np.arange(1,7,1), np.concatenate((np.array(household_sizes)[np.arange(0,5,1)], ['6+'])) )
plt.xlabel('Household size')
plt.ylabel('Density')
plt.title('Distribution of household size')
plt.grid(True)
plt.savefig('household_size')
plt.show()
plt.close()

WP_ranges = workplace_sizes
WP_numbers = np.array([len(workplaces.loc[workplaces['number of people']==WP_ranges[i]]) for i in range(0,len(WP_ranges))])
#WP_capacity = np.array([len(workplaces.loc[workplaces['capacity']==WP_ranges[i]]) for i in range(0,len(WP_ranges))])
#WP_capacity = WP_capacity/sum(WP_capacity)
WP_output_distribution = WP_numbers/sum(WP_numbers)
workplace_distribution = p_n
plt.plot(np.log(workplace_sizes), np.log(workplace_distribution))
plt.plot(np.log(workplace_sizes),np.log(WP_output_distribution),'r')
plt.xlabel('Workplace size (log-scale)')
plt.ylabel('log-Density')
plt.title('Distribution of workplace size (in log-scale)')
plt.grid(True)
plot_xlabel =  [1, 10, 100, 1000, 2400]
#plot_ylabel = [1, 5, 25,  125, 625, 1000, 2400]
plot_xlabel1 = np.log(workplace_sizes)[plot_xlabel]
#plot_ylabel1 = np.log(workplace_distribution[plot_ylabel])
#plt.yticks(plot_ylabel1, workplace_distribution[plot_xlabel])
plt.xticks(plot_xlabel1, (workplace_sizes)[plot_xlabel])
plt.savefig('before_down')
plt.show()
plt.close()

# create workplace distances