
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

YELP_API_KEY = secrets.YELP_API_KEY
MAPQUEST_API_KEY = secrets.MAPQUEST_API_KEY
CACHE_FILENAME = "final_project_cache.json"
CACHE_DICT = {}

def get_yelp_data(location, latitude, longitude, food_input):

    headers = {'Authorization': 'Bearer %s' % YELP_API_KEY}
    url='https://api.yelp.com/v3/businesses/search'
    
    if location == "NA":
        params = {'term':food_input,'latitude': latitude,'longitude': longitude,'limit': 5, 'sortby': 'rating'}
 
    else:
        params = {'term':food_input,'location':location,'limit': 5,'sortby': 'rating'}
    
    response_url = str(location) + str(latitude) + str(longitude) + str(food_input)
    count = 1
    restaurant_name = []
    url_list = []

    if response_url in CACHE_DICT.keys():
        print("Using Cache")
    
    else:
        print("Fetching")
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

    for i in CACHE_DICT[response_url]:
        name = i['name']
        print(count, name)
        count += 1
        restaurant_name.append(name)

    for i in CACHE_DICT[response_url]:
        url_list.append(i['url'])

    return url_list

def scrape_yelp(url_list, choice_input):

    url = url_list[choice_input-1]

    if url in CACHE_DICT.keys():
        print("Using Cache")
    
    else:
        print("Fetching")
        response = requests.get(url)
        CACHE_DICT[url] = response.text
        save_cache(CACHE_DICT)
    
    soup = BeautifulSoup(CACHE_DICT[url], 'html.parser')
    desc = soup.find(class_="margin-t3__373c0__1l90z border-color--default__373c0__3-ifU")
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
    
    user_input = re.sub(r'[^a-zA-Z]',r'',user_input)
    user_input = user_input.lower()
    user_input = user_input.strip()
    return user_input

def get_coords(city, state):

    url = ('https://www.mapquestapi.com/geocoding/v1/address?key=' + MAPQUEST_API_KEY + '&inFormat=kvp&outFormat=json&location=' + str(city) + "+" + str(state) + '&thumbMaps=false')

    if url in CACHE_DICT.keys():
        print("Using Cache")

    else:
        print("Fetching")    
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
    print("To begin, the program will show you the top 10 rated restaurants based on your preferences.")
    print("\n")
    choice_input = ""

    while True:
        if choice_input == "exit":
            break

        user_input = str(input("Please enter a Zip Code. If you do not know the respective Zip Code, please enter \'1' to enter the City & State or \'exit' to quit: "))

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
            food_input = str(input("Please enter the food category, or \'exit' to quit: "))
            food_input = check_input(food_input)
            print("\n")

            if food_input == "exit":
                print("Bye!")
                print("\n")
                break

            if user_input != 1:
                user_zipcode = user_input
                latitude_coord = "NA"
                longitude_coord = "NA"
            else:
                latitude_coord, longitude_coord = get_coords(city_input, state_input)
                user_zipcode = "NA"
                user_input = city_input + ", " + state_input
            
            print("The top 5 rated", food_input, "resturants in", user_input, "are:")

            choice_input = ""

            while True:
                if choice_input == "back" or choice_input == "exit":
                    break

                url_list = get_yelp_data(user_zipcode, latitude_coord, longitude_coord, food_input)

                if len(url_list) == 0:
                    break

                else:
                    print("\n")


                while True:
                    choice_input = str(input("To view the menu of one of the restaurants listed above, please either enter the corresponding list number, enter \'back' to go to step 1, or enter \'exit': "))
                    print("\n")

                    try:
                        choice_input = int(choice_input)
                        menu_list = scrape_yelp(url_list, choice_input)
                        webbrowser.open(menu_list[0])
                    
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

        except ValueError:
            print("Invalid Input!")
            
            


            



    



 