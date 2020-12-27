from django.shortcuts import render, redirect
from .SpotifyAPI import SpotifyAPI, embedify
import json, requests, random
from .forms import MoodForm
from .models import Mood

ClientID = 'fb1324d95b384e17a6e4838f3ab7cfb8'
ClientSecret = '0ca1f712c71e4afca45509ee6769c2de'
client = SpotifyAPI(ClientID, ClientSecret)

SPOTIFY_API_BASE_URL = "https://api.spotify.com"
API_VERSION = "v1"
SPOTIFY_API_URL = "{}/{}".format(SPOTIFY_API_BASE_URL, API_VERSION)

CLIENT_SIDE_URL = "http://127.0.0.1"
PORT = 5000
REDIRECT_URI = "{}:{}/callback".format(CLIENT_SIDE_URL, PORT)
print(REDIRECT_URI)

def auth(request):
    print(request.method)
    if request.method == 'POST':
        form = MoodForm(request.POST)
        if form.is_valid():
            sad_or_happy = request.POST['sad_or_happy']
            request.session['sad_or_happy'] = sad_or_happy
            print(f'{sad_or_happy} :sad_or_happy')
        else:
            form = MoodForm()  
    return redirect(client.generate_auth_url())

def callback(request):
    client.set_show_dialog_false()

    # Authorization
    auth_token = request.GET['code']
    code_payload = {
        "grant_type": "authorization_code",
        "code": str(auth_token),
        "redirect_uri": REDIRECT_URI,
        'client_id': ClientID,
        'client_secret': ClientSecret,
    }
    post_request = requests.post(client.get_token_url(), data=code_payload)

    # Tokens are Returned to Application
    response_data = json.loads(post_request.text)
    try:
        access_token = response_data["access_token"]
    except KeyError:
        return redirect('/auth')
    refresh_token = response_data["refresh_token"]
    token_type = response_data["token_type"]
    expires_in = response_data["expires_in"]

    # Use the access token to access Spotify API
    authorization_header = {"Authorization": "Bearer {}".format(access_token)}

    # Get profile data
    user_profile_api_endpoint = "{}/me".format(SPOTIFY_API_URL)
    profile_response = requests.get(user_profile_api_endpoint, headers=authorization_header)
    profile_data = json.loads(profile_response.text)

    # Get user playlist data
    playlist_api_endpoint = "{}/playlists".format(profile_data["href"])
    playlists_response = requests.get(playlist_api_endpoint, headers=authorization_header)
    playlist_data = json.loads(playlists_response.text)

    # Combine profile and playlist data to display
    display_arr = [profile_data] + playlist_data["items"]

    # Get tracks
    n = random.randint(1, len(display_arr) - 1)
    playlist_id = display_arr[n]['id']
    tracks_response = requests.get(f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks",
                                   headers=authorization_header)
    tracks_data = json.loads(tracks_response.text)
    try:
        random_track = tracks_data['items'][random.randint(0, len(tracks_data['items']) - 1)]['track']['external_urls'][
        'spotify']
    except TypeError:
        random_track = tracks_data['items'][random.randint(0, len(tracks_data['items']) - 1)]['track']['external_urls'][
        'spotify']
    

    # Turning from this https://open.spotify.com/track/7HKez549fwJQDzx3zLjHKC
    #                           |
    #                           |
    #                           V
    # To This https://open.spotify.com/embed/track/2g8HN35AnVGIk7B8yMucww

    # Get a Random Track in case the user types in nothing
    random_track = embedify(random_track)

    # Profile Picture and Name
    users_name = display_arr[0]['display_name']
    try:
        prof_pic = display_arr[0]['images'][0]['url']
    except:
        prof_pic = "/static/musicplayer/wine.png"
    # Get Audio Features
    
    tracks = []
    for track in tracks_data['items']:        
        try:
            # print(track['track']['id'])
            tracks.append(track['track']['id'])
        except TypeError:
            pass
    # Random Comment

    # Obtain Audio Features For the Songs
    audio_features = client.get_audio_features(auth_header=authorization_header, track_ids=tracks)

    # Speech Recognizer
    # run_speech_recognizer()
    
    # Analyze user answers
    sad_or_happy = request.session.get('sad_or_happy')
    print(sad_or_happy)
    if sad_or_happy is not None:
        if 'sad' in sad_or_happy:
            random_track = client.get_low_valence_songs(audio_features)
        if 'happy' in sad_or_happy:
            random_track = client.get_high_valence_songs(audio_features)
        sad_or_happy = None
    context= {
        'prof_pic': prof_pic,
        'random_track': random_track,
        'users_name': users_name,
    }
    return render(request, "spotify/main.html", context)