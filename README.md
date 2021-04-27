# Welcome to my Final Project!

This project will allow a user to:

(1) Enter a zipcode or city & state to then see four visualizations of restaurants in the area based on Yelp's API data.
(2) Then, the user can narrow their search by entering a food category to see the top 10 rated restaurants in that area within this food category.
(3) Lastly, the user can choose to look at a menu of one of the top 10 rated restaurants in to learn more.

In order to run this code, the user will need to obtain API keys from Yelp Fusion and Mapquest. The instructions for how to do so are shown below:

## Yelp Fusion API Keys Instructions:

(1) Go to https://www.yelp.com/developers/documentation/v3/authentication
(2) In order to set up your access to Yelp Fusion API, you need to create an app with Yelp.
(3) To create an app, go to https://www.yelp.com/developers/v3/manage_app
(4) In the create new app form, enter information about your app, then agree to Yelp API Terms of Use and Display Requirements. 
(5) Then click the Submit button. You will now have an API Key. Remember to keep the API Key to yourself since it is the credential for your call to Yelp's API.

## Mapquest API Keys Intructions:

(1) Go to https://developer.mapquest.com/plan_purchase/steps/business_edition/business_edition_free/register
(2) Follow the steps on the website above to register for an account.
(3) Once you have created an account, you will be prompted to a new screen. On this screen, click the button that says 'Create a New Key'.
(4) You will then need to create an App Name. For the sack of my project, you can enter 'Sarah Fringer Final Project'.
(5) Then click the 'Create App' button and you will be given an API Key. Remember to keep the API Key to yourself since it is the credential for your call to Mapquest's API.

## Install Python Packages

The packages that need to be installed for this project are shown below:

* from bs4 import BeautifulSoup
* requests
* re
* json
* webbrowser
* secrets
* sqlite3
* plotly.graph_objs as go
* pandas as pd
* plotly.subplots import make_subplots

