
#################################
##### Name: Sarah Fringer
##### Uniqname: sfringer
#################################

from bs4 import BeautifulSoup
import requests
import re
import json
import webbrowser
import secrets
import sqlite3
import plotly.graph_objs as go
import pandas as pd
from plotly.subplots import make_subplots

YELP_API_KEY = secrets.YELP_API_KEY
MAPQUEST_API_KEY = secrets.MAPQUEST_API_KEY
CACHE_FILENAME = "final_project_cache.json"
CACHE_DICT = {}

def get_yelp_data(location, latitude, longitude, food_input):
    ''' This function takes the user's search criteria and makes a request 
    to the Web API using the parameters given by the user. Then, the 
    functions checks the cache for a saved result for these parameter values. 
    If the result is found, return it. Otherwise send a new 
    request, save it, then return it. This function will then print 
    out the top 10 rated restaurants in the area, provided by the user, based on
    the food category they wanted to look at. 

        Parameters
        ----------
        location: int/str
                The zipcode of the location that the user entered. This can be a str in the value
                is NA or an int if the user actually entered a zipcode.

        latitude: str
                The latitude coordinate of the location that the user entered.

        longitude: str
                The longitude coordinate of the location that the user entered.

        food_input: str
                The food category that the user entered.


        Returns
        -------
        url_list: list
                This list hold every Yelp url of the results that meet the user's search criteria. 

        response_url_list: list
                This list holds made up strings based on the user's search critera. This list holds
                importance when searching through the json cache file later on in the program.
        
        '''

    headers = {'Authorization': 'Bearer %s' % YELP_API_KEY}
    url='https://api.yelp.com/v3/businesses/search'
    response_url_list = []
    
    for offset in [0,50]:
        if location == "NA" and food_input != "NA":
            params = {'term':food_input,'latitude': latitude,'longitude': longitude,'limit': 50, 'sortby': 'rating', 'offset': offset, 'categories': 'restaurants'}

        elif location == "NA" and food_input == "NA":
            food_input = "food"
            params = {'term': food_input,'latitude': latitude,'longitude': longitude,'limit': 50, 'sortby': 'rating', 'offset': offset, 'categories': 'restaurants'}
        
        elif location != "NA" and food_input == "NA":
            food_input = "food"
            params = {'term': food_input,'location':location,'limit': 50, 'sortby': 'rating', 'offset': offset, 'categories': 'restaurants'}

        else:
            params = {'term':food_input,'location':location,'limit': 50,'sortby': 'rating','offset': offset, 'categories': 'restaurants'}

        response_url = str(location) + str(latitude) + str(longitude) + str(food_input) + str(offset)
        response_url_list.append(response_url)
        count = 1
        restaurant_name = []
        url_list = []

        if response_url in CACHE_DICT.keys():
            print("")
        
        else:
            req = requests.get(url, params=params, headers=headers)
            json_dict = json.loads(req.text)

            if (list(json_dict.keys())[0]) == "error":
                print("\n")
                print("There are no searches with your criteria. Please try again.")
                url_list = []
                return url_list

            else:
                json_results = json_dict['businesses']
                CACHE_DICT[response_url] = json_results
                save_cache(CACHE_DICT)

    if food_input == "food":
        print("")

    else:
        for i in CACHE_DICT[response_url][:10]:
            name = i['name']
            print(count, name)
            count += 1
            restaurant_name.append(name)

    for i in CACHE_DICT[response_url]:
        url_list.append(i['url'])

    return url_list, response_url_list

def create_sql_table(response_url_list, user_input, user_zipcode):
    ''' This function creates the database that I use for my visualizations.
    It creates a database through SQL functions. The database is called Final_Project.sqlite and
    the table is called 'yelp'. The table has 6 columns: ID, Location, Rating, Category, Price, Name.
    This table is created when the user enters which location that are interested in viewing Yelp
    data for. This data is then stored into the table. 100 rows are generated per location request of 
    the user.
    
    Parameters
    ----------
    response_url_list: list
            This list is used to better search through the json cache file. 
            This function will iterate through this list to find the values
            stored in the cache file. Again, this list contains unique made-up strings
            per search request made by the user.

   user_input: str
            This is the location string that the user has inputted into the program. This is used
            as the location variable if the user does not enter a zipcode.
    
    user_zipcode: int/str
            This is the zipcode of the location that the user has inputted into the program. 
            This is used as the location variable if the user does not enter a city & state. This is 
            an int is the user enters a zipcode and is NA is the user does not.
    
    Returns
    -------
    NA
    '''

    conn = sqlite3.connect("Final_Project.sqlite")
    cur = conn.cursor()

    drop_table = '''
        DROP TABLE IF EXISTS "yelp";
    '''

    cur.execute(drop_table)

    create_table = '''
        CREATE TABLE IF NOT EXISTS "yelp" (
            "ID"        INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
            "Location"  TEXT NOT NULL,
            "Rating"    INTEGER,
            "Category"  TEXT,
            "Price"     TEXT,
            "Name"      TEXT
        );
    '''

    cur.execute(create_table)
    conn.commit()

    insert_table = '''
        INSERT INTO "yelp"
        VALUES (NULL, ?, ?, ?, ?, ?)
    '''

    if user_zipcode == "NA":
        location = user_input
    else:
        location = user_zipcode

    for j in response_url_list:
        for i in CACHE_DICT[j]:
            rating = i['rating']
            category = i['categories']
            category = category[0]
            category = category['alias']
            name = i['name']

            if 'price' not in i.keys():
                price = "NA"
            else:
                price = i['price']

            yelp_values = [location, rating, category, price, name]
            cur.execute(insert_table, yelp_values) 
            conn.commit()

def create_plots(user_input, user_zipcode):
    ''' This function plots 4 plotly visualizations. Specifically it plots 3 bar charts
    and 1 histogram. Barchat #1: The average rating per food based on the user's location of choice.
    Barchart #2: The distribution of different priced restaurants based on the user's location of choice.
    Histogram #1: The distribution of ratings based on the user's location of choice.
    Barchart #3: The number of restaurants in each food category based on the user's location of choice.
    This function takes the data from the sql table created in the create_sql_table function. 
    
    Parameters
    ----------
    user_input: str
            This is the location string that the user has inputted into the program. This is used
            to be put in the title of the plots. 
    
    user_zipcode: int/str
            This is the zipcode of the location that the user has inputted into the program. This is
            used to be put into the title of the plots. This is an int is the user enters a zipcode and 
            is NA is the user does not.
    
    Returns
    -------
    NA
    '''

    if user_zipcode == "NA":
        location = user_input
    else:
        location = user_zipcode
    conn = sqlite3.connect("Final_Project.sqlite")

    dataframe = pd.read_sql("""
                SELECT *
                FROM yelp
                """, con = conn)

    fig = make_subplots(rows=4, cols=1, subplot_titles=("Average Rating per Food Category in " + str(location), "The Number of Priced Restaurants in " + str(location), "Distribution of Ratings in " + str(location), "How Many Restaurants are in Each Category in " + str(location)))

    plt1 = dataframe.groupby('Category').mean()
    plt1 = plt1.drop(['ID'], axis=1)
    plt1 = plt1.reset_index()

    plt2 = dataframe['Price'].value_counts()
    plt2 = pd.DataFrame(plt2)
    plt2 = plt2.drop('NA')
    plt2 = plt2.reset_index()

    plt3 = dataframe['Category'].value_counts()
    plt3 = pd.DataFrame(plt3)
    plt3 = plt3.reset_index()
  
    fig.add_trace(go.Bar(x=plt1['Category'], y=plt1['Rating']), row=1, col=1)
    fig.add_trace(go.Bar(x=plt2['index'], y=plt2['Price']), row=2, col=1)
    fig.add_trace(go.Histogram(x=dataframe['Rating']), row=3, col=1)
    fig.add_trace(go.Bar(x=plt3['index'], y=plt3['Category']), row=4, col=1)

    fig.show()

def scrape_yelp(url_list, choice_input):
    ''' This function scarpes Yelp's website to find the link of the menu of a given restaurant.
    The user will be given a list of the top 10 rated restaurants in the area. The user 
    can they choose to view a menu from one of the restaurants on the list. This function
    scrapes Yelp's website to find the correct link. This link will then open for the user in 
    a browser for them to then view.
    
    Parameters
    ----------
    url_list: list
            This is list given to the user of the top 10 rated restaurants in the area
            they provided.
    
    choice_input: int
            This is the number that the user enters. This number corresponds to the number
            is the list printed to the user, showing the top 10 rated restaurants in the area. 
    
    Returns
    -------
    menu_list: list
            This contains the link with the menu that the user requested to see.

    '''

    url = url_list[choice_input-1]

    if url in CACHE_DICT.keys():
        print("")
    
    else:
        response = requests.get(url)
        CACHE_DICT[url] = response.text
        save_cache(CACHE_DICT)
    
    soup = BeautifulSoup(CACHE_DICT[url], 'html.parser')
    desc = soup.find(class_="margin-t3__373c0__1l90z border-color--default__373c0__2oFDT")
    menu_list = []

    for a in desc.find_all('a', href=True):
        menu_list.append(a['href'])
    
    if 'https' not in menu_list[0] and 'http' not in menu_list[0]:
        print("I'm sorry! Yelp does not have a menu for this restaurant. Yelp Website's for this restaurant will open for you instead. ")
        print("\n")
        menu_list = []
        menu_list.append(url)
    
    return menu_list

def check_input(user_input):
    ''' This function checks the user's input. This function
    will remove any integer values from the string and replace it 
    with a blank space. Then it will lower all the letters and strip the
    string from any white space.
    
    Parameters
    ----------
    user_input: str
            This is the string the user types into the program.
    
    Returns
    -------
    user_input: str
            This is the newly improved string that has been cleaned and revised. 
    '''
    
    user_input = re.sub(r'[^a-zA-Z]',r'',user_input)
    user_input = user_input.lower()
    user_input = user_input.strip()
    return user_input

def get_coords(city, state):
    ''' This function gets the latitude and longitude coordinates of the city and state the user
    enters. This function is able to do this by connecting to Mapquest's API. The
    function checks the cache for a saved result for the city and state values. 
    If the result is found, return it. Otherwise send a new 
    request, save it, then return it. This function is needed because if the user chooses
    to enter a city and state rather than a zipcode, the Yelp request will not work. 
    Therefore, we need to get the respective coordinates to send a successful request. 
    
    Parameters
    ----------
    city: str
            This is the city the user types into the program.
    
    state: str
            This is the state the user types into the program.
    
    Returns
    -------
    latitude_coord: str
            This is the corresponding latitude value to the city and state the user entered,
            based on the results from Mapquest's API. 

    longitude_coord: str
            This is the corresponding longitude value to the city and state the user entered,
            based on the results from Mapquest's API. 
    '''

    url = ('https://www.mapquestapi.com/geocoding/v1/address?key=' + MAPQUEST_API_KEY + '&inFormat=kvp&outFormat=json&location=' + str(city) + "+" + str(state) + '&thumbMaps=false')

    if url in CACHE_DICT.keys():
        print("")

    else:
        mapquest_req = requests.get(url)
        json_dict = json.loads(mapquest_req.text)
        json_results = json_dict['results']
        CACHE_DICT[url] = json_results
        save_cache(CACHE_DICT)

    for j in CACHE_DICT[url]:
        loc = j['locations']
        loc_values = loc[0]
        location = loc_values['latLng']
        latitude_coord = location['lat']
        longitude_coord = location['lng']

    return latitude_coord, longitude_coord

def open_cache():
    ''' Opens the cache file if it exists and loads the JSON into
    the CACHE_DICT dictionary.
    if the cache file doesn't exist, creates a new cache dictionary
    
    Parameters
    ----------
    None
    
    Returns
    -------
    The opened cache: dict
    '''
    try:
        cache_file = open(CACHE_FILENAME, 'r')
        cache_contents = cache_file.read()
        cache_dict = json.loads(cache_contents)
        cache_file.close()
    except:
        cache_dict = {}
    return cache_dict

def save_cache(cache_dict):
    ''' Saves the current state of the cache to disk
    
    Parameters
    ----------
    cache_dict: dict
        The dictionary to save
    
    Returns
    -------
    None
    '''
    dumped_json_cache = json.dumps(cache_dict)
    fw = open(CACHE_FILENAME,"w")
    fw.write(dumped_json_cache)
    fw.close() 
    

if __name__ == "__main__":
    CACHE_DICT = open_cache()
    print("\n")
    print("#################################################################")
    print("Welcome to the program! This is a program regarding Yelp Reviews!")
    print("#################################################################")
    print("\n")
    print("To begin, the program will show you 4 visualizations on Yelp Data!")
    print("\n")
    choice_input = ""
    food_input = "NA"

    while True:
        if choice_input == "exit":
            break

        user_input = str(input("Please enter a Zip Code. If you do not know the respective Zip Code, please enter \'1' to enter the City & State or \'exit' to quit:  "))

        food_input = "NA"

        if user_input != "exit" and user_input == "1":
            city_input = str(input("Please enter the City: "))
            city_input = check_input(city_input)
            state_input = str(input("Please enter the State: "))
            state_input = check_input(state_input)

        if user_input == "exit":
            print("Bye!")
            print("\n")
            break

        try:
            user_input = int(user_input)

            if user_input != 1:
                user_zipcode = user_input
                latitude_coord = "NA"
                longitude_coord = "NA"
            else:
                latitude_coord, longitude_coord = get_coords(city_input, state_input)
                user_zipcode = "NA"
                user_input = city_input + ", " + state_input

            url_list, response_url = get_yelp_data(user_zipcode, latitude_coord, longitude_coord, food_input)
            create_sql_table(response_url, user_input, user_zipcode)
            create_plots(user_input, user_zipcode)

            food_input = str(input("Now please enter a food category to learn more about the 10 top rated restaurants within this category, based upon the location you specified in part 1, or \'exit' to quit: "))
            food_input = check_input(food_input)
            print("\n")

            if food_input == "exit":
                print("Bye!")
                print("\n")
                break

            print("The top 10 rated", food_input, "resturants in", user_input, "are:")
            
            choice_input = ""

            while True:
                if choice_input == "back" or choice_input == "exit":
                    break

                url_list, response_url = get_yelp_data(user_zipcode, latitude_coord, longitude_coord, food_input)

                if len(url_list) == 0:
                    print("There are no restaurants in this area with that food category.")
                    print("\n")
                    break

                else:
                    print("\n")

                while True:
                    choice_input = str(input("To view the menu of one of the restaurants listed above, please either enter the corresponding list number, enter \'back' to go to step 1, or enter \'exit': "))
                    print("\n")

                    try:
                        choice_input = int(choice_input)

                        if choice_input <= 10 and choice_input > 0:
                            menu_list = scrape_yelp(url_list, choice_input)
                            webbrowser.open(menu_list[0])
                        
                        else:
                            print("Invalid Input. Please enter a number on the list.")
                            print("\n")
                    
                    except ValueError:
                        choice_input = check_input(choice_input)
                        if choice_input == "exit":
                                print("Bye!")
                                print("\n")
                                break
                            
                        elif choice_input == "back":
                            break
                        
                        else:
                            print("[Error] Invalid Input")
                            print("\n")

        except ValueError:
            print("Invalid Input!")
            
            


            



    



 