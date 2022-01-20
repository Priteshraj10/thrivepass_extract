import pandas as pd
import openpyxl
from datetime import datetime, date

df = pd.read_excel('data/orignal_testing_data/QB Summary 2021.11.10 raw-test.xlsx')

# str contains method
mask = df[df['Member Information'].str.contains(r"MemberID", na=False)]

# indexes of mask
indexes = mask.index.values

# member information dataframe
member_df = df.iloc[indexes[0]:indexes[1]-3]
print(member_df)

# plan information dataframe
plan_df = df.iloc[indexes[1]:indexes[2]-3]
#print(plan_df)

# sort dataframe by MemberID
# member_df = member_df.sort_values(by=['MemberID'])

# concat member_df and plan_df
# final_df = pd.concat([plan_df, member_df], keys=['MemberID'])
# final_df = pd.merge(plan_df,member_df,on='MemberID', how='inner')

# Final dataframe
# final_df = pd.merge(plan_df,member_df,sort=True,on='MemberID', suffixes=('', '_delme'), how='outer')
# final_df = final_df[[c for c in final_df.columns if not c.endswith('_delme')]]

# print(final_df.columns)

"""
# Age conversion to years from DOB
def age(born):
    born = datetime.strptime(str(born), "%Y-%m-%d %H:%M:%S").date()
    today = date.today()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))

# DOB to age conversion
member_df['Age'] = member_df['DOB'].apply(age)
"""

# Dependent And Dependent Plan Information
dependent_df = df.iloc[indexes[4]:]
# print(dependent_df)

"""
# Age conversion to years from DOB
def dep_age(born):
    born = datetime.strptime(str(born), "%d-%m-%Y %H:%M:%S").date()
    today = date.today()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))
"""

# Age conversion to years from DOB
# dependent_df['Dep_Age'] = dependent_df['DOB'].apply(dep_age)

# pd.DataFrame.to_excel(data_plan, 'data/orignal_testing_data/plan_df_slice.xlsx', header=None)
"""
# merge the two dataframes with member id
final_df = pd.merge(plan_df, member_df, on='MemberID', suffixes=('', '_delme'))
final_df = final_df[[c for c in final_df.columns if not c.endswith('_delme')]]
"""
