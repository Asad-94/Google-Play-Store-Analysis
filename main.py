# importing Libraries
from flask import Flask, render_template, request
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import random
from numerize import numerize
import warnings; 
warnings.filterwarnings('ignore')

app = Flask(__name__)

# Removing cache for images
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0


# Reading Dataset outside the route to load the dataset on app run
df = pd.read_csv('Google-Playstore.csv')


# Select your desired category from the list
select_options = df['Category'].value_counts().index

# All tasks are loading only on the start of app
# 1) How many apps are paid and how many are free?

df_true = df[df['Free'] == True]['Free']
df_false = df[df['Free'] == False]['Free']

free_apps = df_true.count()
paid_apps = df_false.count()

percentage_of_free_apps = (free_apps)/(free_apps+paid_apps)*100
percentage_of_paid_apps = (paid_apps)/(free_apps+paid_apps)*100


# 2) How many apps are Ad-supported and how many aren't?

df_true_ad_supported = df[df['Ad Supported'] == True]['Ad Supported']
df_false_ad_supported = df[df['Ad Supported'] == False]['Ad Supported']

ad_supported_apps = df_true_ad_supported.count()
non_ad_supported_apps = df_false_ad_supported.count()

percentage_of_ad_supported_apps = ad_supported_apps/(ad_supported_apps+non_ad_supported_apps)*100
percentage_of_non_ad_supported_apps = non_ad_supported_apps/(ad_supported_apps+non_ad_supported_apps)*100


# 3) How many apps are released per year?

df_clean_released_column = df[df['Released'].notna()][['Released']]

def split_in(x):
    a = str(x).split(' ')
    return a[-1]

df_clean_released_column['Year'] = df['Released'].apply(split_in)

year_wise_add = df_clean_released_column.groupby('Year').count()

x = year_wise_add.index
y = year_wise_add['Released']
plt.figure(figsize=(16,7), facecolor='#F0FFFF')
plt.xlabel('Year',  fontsize=25, labelpad=25)
plt.ylabel('App Count (in Millions)', fontsize=25,  labelpad=25)
plt.title('App Count Per Year', fontsize=22)
plt.xticks(fontsize=15)
plt.yticks(fontsize=20)

plt.plot(x, y, marker='o', linewidth=3, markersize=10, color='#088F8F')
plt.savefig('static/app_count_per_year.png', bbox_inches = 'tight')


# 4) Which app has been downloaded the most?

df_most_download_apps = df.sort_values('Maximum Installs', ascending=False)[['App Name', 'Maximum Installs']].head(10)

plt.figure(figsize=(16,8), facecolor='#F0FFFF')
plt.yticks(fontsize=18)
plt.xticks(rotation=60, fontsize=18)
plt.xlabel('App Name', fontsize=18, labelpad=25)
plt.ylabel('Download Count (in Billions)', fontsize=25, labelpad=25)
plt.title('Top 10 Most Downloaded Apps', fontsize=22)
x = ['Google Play services','YouTube', 'Google', 'Google Maps' ,'Google Text-to-Speech' ,'Google Chrome' ,'Gmail' 
        ,'Android Suite', 'Google Drive' ,'Facebook']
y = df_most_download_apps['Maximum Installs']

plt.bar(x,y, color='#088F8F')
plt.savefig('static/most_downloaded_apps.png', bbox_inches = 'tight')


# 5) How many users have responded (given rating) to the apps in a particular year?

df_clean_released_column_2 = df[(df['Rating Count'].notna()) & (df['Released'].notna())][['Rating Count', 'Released']]
df_clean_released_column_2['Year'] = df['Released'].apply(split_in)
year_wise_add_2 = df_clean_released_column_2.pivot_table(index=['Year'],aggfunc=np.sum)
plt.figure(figsize=(18,8), facecolor='#F0FFFF')
plt.xlabel('Year',  fontsize=25, labelpad=25)
plt.ylabel('User Count (in Millions)', fontsize=25, labelpad=25)
plt.title('User Count Per Year', fontsize=25)
plt.xticks(fontsize=25, rotation=40)
plt.yticks(fontsize=25)
plt.plot(year_wise_add_2.index,year_wise_add_2['Rating Count'], marker = 'o', linewidth=3, markersize=10, color='#088F8F' )
plt.savefig('static/user_count_per_year.png', bbox_inches = 'tight')


# 6) Quality level of applications based on good, average, or poor as rated by the users.

clean_rating_column = df[df['Rating'].notna()]
def convert_me(x):
    if x >= 4.5:
        return 'Good'
    elif x >= 3.0:
        return 'Average'
    else:
        return 'Poor'
    
df['Rating text'] = df['Rating'].apply(convert_me)
app_rating_count = df['Rating text'].value_counts()


x = app_rating_count.index
y = app_rating_count.values

quality_rating = []

for i in range(0,len(x)):
    total = round(y[i]/sum(y)*100, 2)
    quality_rating.append((x[i], total))


# 7) Which category is more popular among the users?

df_category_wise = df.pivot_table(index=['Category'], aggfunc=np.sum)
df_category_wise_2 = df_category_wise['Maximum Installs'].sort_values(ascending=False)[0:10]

x = df_category_wise_2.index
y= df_category_wise_2.values

plt.figure(figsize=(16,8), facecolor='#F0FFFF')
plt.xlabel('Category',  fontsize=25, labelpad=25)
plt.ylabel('Download Count (in billions)', fontsize=25, labelpad=25)
plt.title('Top 10 Most Popular Categories', fontsize=22)
plt.xticks(rotation=60, fontsize=15)
plt.yticks(fontsize=20)

plt.bar(x,y, color='#088F8F')
plt.savefig('static/most_popular_categories.png', bbox_inches = 'tight')


# 8) Top & Bottom-most app categories with respect to Average Rating.

average_rating_category_based = df.groupby('Category').mean()['Rating'].sort_values(ascending=False)

x = average_rating_category_based[:5].index
y = average_rating_category_based[:5].values

top5_rating_based_apps = []

for i in range(0, len(x)):
    rating = round(y[i], 1)
    top5_rating_based_apps.append((x[i], rating))


x = average_rating_category_based[-5:].index
y = average_rating_category_based[-5:]

bottom5_rating_based_apps = []

for i in range(0, len(x)):
    rating = round(y[i], 1)
    bottom5_rating_based_apps.append((x[i], rating))


# 9) Top 10 fast growing apps since January, 2020.

df_recent_famous_app = df[(df['Released'].notna())]
df_recent_famous_app_2 = df_recent_famous_app[(df['Released'].str.contains('2020'))  | 
                                            (df['Released'].str.contains('2021'))][['App Name', 'Maximum Installs', 'Released']]

df_maximum_Installs_sorted = df_recent_famous_app_2.sort_values('Maximum Installs', ascending=False)[0:10]

x = df_maximum_Installs_sorted['App Name']
y = df_maximum_Installs_sorted['Maximum Installs']

top_most_downloads_recent = []

top_most_downloads_recent_names = ['Samsung Members', 'Samsung Display', 'Weather - By Xiaomi', 'HUAWEI Video', 'Google Pay', 
                                   'Microsoft Office', 'Mi Browser Pro', 'Moto Widget', 'My Talking Tom Friends', 'Mi Calendar']

for i in range(0, len(x)):
    top_most_downloads_recent.append((x.values[i], numerize.numerize(float(y.values[i]))))


# 10) Most expensive and cheapest apps.

df_paid_apps = df[(df['Free'] == False) & df['Price'] != 0.00].sort_values('Price')
cheapest_apps = df_paid_apps.iloc[0:2][['App Name', 'Price']].values
most_expensive_app = df_paid_apps.iloc[-1][['App Name', 'Price']].values

cheapest_apps[0][1] = round(cheapest_apps[0][1],3)
cheapest_apps[1][1] = round(cheapest_apps[1][1],3)


# 11) Rating History of Play Store.

df_without_released_null = df[df['Released'].notna()]

df_without_released_null ['Year'] = df_without_released_null['Released'].apply(split_in)

df_mean_rating = df_without_released_null.pivot_table(index=['Year'], aggfunc=np.mean)

x = df_mean_rating.index
y = df_mean_rating.Rating

plt.figure(figsize=(18,8), facecolor='#F0FFFF')
plt.xlabel('Year',  fontsize=25, labelpad=25)
plt.ylabel('Average Rating', fontsize=25, labelpad=25)
plt.title('Average Rating Per Year', fontsize=25)
plt.xticks(fontsize=15)
plt.yticks(fontsize=20)

plt.plot(x,y, marker = 'o', linewidth=3, markersize=10, color='#088F8F' )
plt.savefig('static/average_rating_per_year.png', bbox_inches = 'tight')


# 12) Which apps are secured (https) and which aren't (http)?

df_secured_website_or_not = df[df['Developer Website'].notna()]

def split_in(x):
    a = str(x).split(':')
    return a[0]

df_secured_website_or_not['Link'] = df_secured_website_or_not['Developer Website'].apply(split_in)

df_secured_website_https = df_secured_website_or_not[df_secured_website_or_not['Link'] == 'https']['Developer Website'].count()
df_secured_website_http = df_secured_website_or_not[df_secured_website_or_not['Link'] == 'http']['Developer Website'].count()

ratio_of_https_apps = df_secured_website_https/(df_secured_website_https+df_secured_website_http)*100
ratio_of_http_apps = df_secured_website_http/(df_secured_website_https+df_secured_website_http)*100


plt.figure(figsize=(16,10))
x = np.array([ratio_of_http_apps, ratio_of_https_apps])
plt.title('Percentage Distribution of Secured and Non Secured Apps', fontsize=25)

plt.pie(x, autopct='%1.2f%%', textprops={'fontsize': 40}, colors =['#2cc3f2','#f6716a'])
plt.legend(labels = ['Non Secured Apps','Secured Apps'], fontsize=25, loc='best')
plt.savefig('static/secured_and_non_secured_apps.png', bbox_inches = 'tight', pad_inches=0, dpi=1000)


# Index route
@app.route("/")
def index():
    return render_template('index.html')

# Dashboard route
@app.route("/dashboard", methods=['GET','POST'])
def dashboard():

    # task 1 and 2 in a list
    output_list = [round(percentage_of_free_apps,2), round(percentage_of_paid_apps,2), round(percentage_of_ad_supported_apps,2), round(percentage_of_non_ad_supported_apps,2), cheapest_apps, most_expensive_app]

    # Features submit form 
    if request.method == 'POST':
        searched_app = df
        x = request.form

        # If Feature 1 executed
        if x['choose category'] != 'none':
            random_number = str(random.randint(0,100))

            my_input_category = x['choose category']
            starting_year = x['starting year']
            ending_year = x['ending year']

            category_data = df[df['Category'] == my_input_category]

            def split_in(x):
                a = str(x).split(' ')
                return a[-1]

            df_without_released_null = category_data[category_data['Released'].notna()]

            df_without_released_null ['Year'] = df_without_released_null['Released'].apply(split_in)

            df_mean_rating = df_without_released_null.pivot_table(index=['Year'], aggfunc=np.mean)
            df_mean_rating = df_mean_rating[(df_mean_rating.index >= starting_year) & (df_mean_rating.index <= ending_year)]

            x = df_mean_rating.index
            y = df_mean_rating.Rating


            plt.figure(figsize=(16,7), facecolor='#F0FFFF')
            plt.xlabel('Years', fontsize=25, labelpad=25)
            plt.ylabel('Average Rating', fontsize=25, labelpad=25)
            plt.title('Average Rating Per Year', fontsize=25)
            plt.xticks(fontsize=15)
            plt.yticks(fontsize=20)
            plt.plot(x, y, marker = 'o', linewidth=3, color='#088F8F', markersize=10)
            plt.savefig('static/feature' + random_number + '.png', bbox_inches = 'tight')


            return render_template('dashboard.html', output_this = 'true', random_number = random_number, 
            select_options = select_options, 
            quality_rating = quality_rating, 
            top5_rating_based_apps = top5_rating_based_apps,
            bottom5_rating_based_apps = bottom5_rating_based_apps, 
            top_most_downloads_recent = top_most_downloads_recent, 
            output_data = output_list,
            top_most_downloads_recent_names = top_most_downloads_recent_names, show_feature1_image = 'true')


        # If Feature 2 executed
        elif x['searchedapp'] != '':

            my_input = x['searchedapp']

            def my_func(x):
                a = str(x).split(' ')
                a = a[0]
                aa = a[0:3]
                return aa

            searched_app['Android Column'] = df['Minimum Android'].apply(my_func)

            data_android_version_2 = searched_app[~(searched_app['Android Column'].str.contains('nan'))]

            searched_android_version = data_android_version_2[data_android_version_2['App Name'] == my_input]

            searched_app_list = [searched_android_version['App Name'].values[0], searched_android_version['Size'].values[0], searched_android_version['Rating'].values[0], searched_android_version['Category'].values[0], 
            searched_android_version['Released'].values[0], searched_android_version['Android Column'].values[0]]

            return render_template('dashboard.html', output_app = searched_app_list, 
            output_this = 'true', 
            select_options = select_options, 
            quality_rating = quality_rating, 
            top5_rating_based_apps = top5_rating_based_apps, 
            bottom5_rating_based_apps = bottom5_rating_based_apps, 
            top_most_downloads_recent = top_most_downloads_recent, 
            output_data = output_list,
            top_most_downloads_recent_names = top_most_downloads_recent_names)

    # Default dashboard when no feature form submit
    else:
        return render_template('dashboard.html' , select_options = select_options, 
        quality_rating = quality_rating, 
        top5_rating_based_apps = top5_rating_based_apps,
        bottom5_rating_based_apps = bottom5_rating_based_apps, 
        top_most_downloads_recent = top_most_downloads_recent, 
        output_data = output_list, 
        top_most_downloads_recent_names = top_most_downloads_recent_names)
        
if __name__ == '__main__':
    app.run()