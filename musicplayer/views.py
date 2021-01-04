from django.shortcuts import render
from .models import Song
import requests, json, csv
from ipstack import GeoLookup
import socket    

geo_lookup = GeoLookup("39f6234e3d9c6d69e5c561c790b129bc")

def home(request):
    location = geo_lookup.get_own_location()
    country = location['country_name']
    flag_link = location['location']['country_flag']
    """
    with open('musicplayer/Country_Flags.csv', 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        for line in csv_reader:
            if country == line[0]:
                flag_link = line[2]
    """
    context= {
        'flag_link': flag_link,
        'country': country,
    }
    return render(request, 'musicplayer/home.html', context)

def about(request):
    return render(request, 'musicplayer/about.html')

def contact(request):
    return render(request, 'musicplayer/contact.html')