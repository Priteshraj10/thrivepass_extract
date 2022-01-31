import pandas as pd
import openpyxl
from datetime import datetime, date, timedelta

df = pd.read_excel('data/orignal_testing_data/QB Summary 2021.11.10 raw-test.xlsx')
"""
# new header for the dataframe
new_header = df.iloc[0] #grab the first row for the header
df = df[1:] #take the data less the header row
df.columns = new_header #set the header row as the df header
"""

# create a function for new header for the dataframe
def new_header(df):
    new_header = df.iloc[0] #grab the first row for the header
    df = df[1:] #take the data less the header row
    df.columns = new_header #set the header row as the df header
    return df

df = new_header(df)

# str contains method
mask = df[df['MemberID'].str.contains(r"MemberID", na=False)]

# indexes of mask
indexes = mask.index.values

# member information dataframe
member_df = df.iloc[0:indexes[0]-3]

# plan information dataframe
plan_df = df.iloc[indexes[0]-1:indexes[1]-3]
plan_df = new_header(plan_df)

"""
# payment information dataframe
pay_df = df.iloc[indexes[1]-1:indexes[2]-3]
pay_df = new_header(pay_df)
print(member_df)
"""

final_df = pd.merge(plan_df,member_df,on='MemberID', how='inner')

# sort by memberid
final_df = final_df.sort_values(by=['MemberID'])

final_df.columns = final_df.columns.fillna('to_drop')
final_df.drop('to_drop', axis=1, inplace=True)


# function pandas datatime
def pandas_datatime(df):
    df['DOB'] = pd.to_datetime(df['DOB'],format='%Y-%m-%d')
    return df


final_df = pandas_datatime(final_df)

input_user = 60

# Age conversion to years from DOB
def dep_age(date):
    born = datetime.strptime(str(date), "%Y-%m-%d %H:%M:%S").date()
    today = date.today()
    sixty_days = today + timedelta(days=input_user)
    return sixty_days.year - born.year - ((sixty_days.month, today.day) < (born.month, born.day))

final_df['Age'] = final_df['DOB'].apply(dep_age)

"""
# 60 days from today
def sixty_days(date):
    today = date.today()
    sixty_days = today + timedelta(days=60)
    return sixty_days
"""

# filter 60 age from the dataframe
final_df = final_df[final_df['Age'] >= input_user]
print(final_df['Age'])

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
dependent_df = df.iloc[indexes[4]-1:]
dependent_df = new_header(dependent_df)
dependent_df.columns = dependent_df.columns.fillna('to_drop')
dependent_df.drop('to_drop', axis=1, inplace=True)
dependent_df.drop('MemberID', axis=1, inplace=True)

# dependent_df = pandas_datatime(dependent_df)


# Age conversion to years from DOB
# dependent_df['Dep_Age'] = dependent_df['DOB'].apply(dep_age)

# pd.DataFrame.to_excel(data_plan, 'data/orignal_testing_data/plan_df_slice.xlsx', header=None)
"""
# merge the two dataframes with member id
final_df = pd.merge(plan_df, member_df, on='MemberID', suffixes=('', '_delme'))
final_df = final_df[[c for c in final_df.columns if not c.endswith('_delme')]]
"""
