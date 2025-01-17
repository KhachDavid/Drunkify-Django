from django.shortcuts import render, redirect, HttpResponse
from .SpotifyAPI import SpotifyAPI
import json, requests, random
from .forms import MoodForm
import speech_recognition as sr

ClientID = 'fb1324d95b384e17a6e4838f3ab7cfb8'
ClientSecret = '0ca1f712c71e4afca45509ee6769c2de'
client = SpotifyAPI(ClientID, ClientSecret)

SPOTIFY_API_BASE_URL = "https://api.spotify.com"
API_VERSION = "v1"
SPOTIFY_API_URL = "{}/{}".format(SPOTIFY_API_BASE_URL, API_VERSION)

CLIENT_SIDE_URL = "http://127.0.0.1"
PORT = 5000
REDIRECT_URI = "{}:{}/callback".format(CLIENT_SIDE_URL, PORT)

def auth(request):
    return redirect(client.generate_auth_url())

def callback(request):
    client.set_show_dialog_false()
    client.empty_the_tracks()

    # Authorization
    auth_token = request.GET.get('code')
    code_payload = {
        "grant_type": "authorization_code",
        "code": str(auth_token),
        "redirect_uri": REDIRECT_URI,
        'client_id': ClientID,
        'client_secret': ClientSecret,
    }
    post_request = requests.post(client.get_token_url(), data=code_payload)
        
    # Tokens are Returned to Application
    flag = False
    while not flag:
        try:
            response_data = json.loads(post_request.text)
            flag = True
        except json.decoder.JSONDecodeError:
            pass
    
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
    try:
        profile_data = json.loads(profile_response.text)
    except json.decoder.JSONDecodeError:
        pass
    
    # Get user playlist data
    playlist_api_endpoint = "{}/playlists".format(profile_data["href"])
    playlists_response = requests.get(playlist_api_endpoint, headers=authorization_header)
    try:
        playlist_data = json.loads(playlists_response.text)
    except json.decoder.JSONDecodeError:
        context= {
            'prof_pic': "/static/musicplayer/wine.png",
            'random_track': 'https://open.spotify.com/embed/track/2g8HN35AnVGIk7B8yMucww',
            'users_name': 'Dashboard',
        }
        return render(request, "spotify/main.html", context)

    # Combine profile and playlist data to display
    display_arr = [profile_data] + playlist_data["items"]

    # Get tracks
    list_of_songs = []
    flag = False
    while not flag:
        try:
            for n in range(1, len(display_arr)):
                playlist_id = display_arr[n]['id']
                tracks_response = requests.get(f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks",
                                            headers=authorization_header)
                try:
                    tracks_data = json.loads(tracks_response.text)
                except json.decoder.JSONDecodeError:
                    pass
                list_of_songs.append(tracks_data)
            flag = True
        except json.decoder.JSONDecodeError:
            pass

    # Profile Picture and Name
    users_name = display_arr[0]['display_name']
    try:
        prof_pic = display_arr[0]['images'][0]['url']
    except:
        prof_pic = "/static/musicplayer/wine.png"
    # Get Audio Features
    tracks = []
    for i in range(len(list_of_songs)):
        for track in list_of_songs[i]['items']:        
            try:
                # print(track['track']['id'])
                tracks.append(track['track']['id'])
            except TypeError:
                pass

    print(f"There are {len(tracks)} songs")
    audio_features = []
    len_of_songs = len(tracks)

    # Obtain Audio Features For the Songs
    if len(tracks) <= 100:
        audio_features = client.get_audio_features(auth_header=authorization_header, track_ids=tracks)
    else:
        while (len_of_songs > 0):
            flag = False
            while not flag:
                try:
                    audio_features_index = client.get_audio_features(auth_header=authorization_header, track_ids=tracks[len_of_songs - 99:len_of_songs] if len_of_songs > 100 else tracks[:len_of_songs])
                    audio_features.append(audio_features_index)
                    len_of_songs = len_of_songs - 100
                    flag = True
                except json.decoder.JSONDecodeError:
                    print(111)
                    pass

    # audio_features['audio_features'][0]['danceability']
    # audio_features['audio_features'][0]['energy']
    request.session['audio_features'] = audio_features
    context= {
        'prof_pic': prof_pic,
        'users_name': users_name,
    }
    return render(request, "spotify/main.html", context)

def update_the_song(request):
    random_track = ''
    if request.method == 'POST':
        sad_or_happy = request.POST.get('sad_or_happy')
        dance_or_no = request.POST.get('dance_or_no')
        tired_or_not = request.POST.get('tired_or_not')
        alone_or_not = request.POST.get('alone_or_not')
        request.session['sad_or_happy'] = sad_or_happy
        request.session['alone_or_not'] = alone_or_not
        request.session['dance_or_no'] = dance_or_no
        request.session['tired_or_not'] = tired_or_not
    
        response_data = {}
        audio_features = request.session.get('audio_features')
        # print(f"{sad_or_happy}: sad_or_happy")
        if sad_or_happy is not None:
            # This is a basic logic implementation to get the website working
            if 'yes' in dance_or_no:
                random_track = client.get_high_danceability_songs(audio_features)
            elif 'sad' in sad_or_happy:
                random_track = client.get_low_valence_songs(audio_features)
            elif 'happy' in sad_or_happy:
                random_track = client.get_high_valence_songs(audio_features)
            sad_or_happy = None

        response_data['random_track'] = random_track
        response_data['flag'] = False
        return HttpResponse(
            json.dumps(response_data),
            content_type="application/json")
    else:
        return HttpResponse(
            json.dumps({"nothing to see": "this isn't happening"}),
            content_type="application/json"
        )

def update_the_command(request):
    random_track = ''
    response_data = {}
    audio_features = request.session.get('audio_features')
    if request.method == 'POST':
        data = request.POST.get('record')
        # Speech Recognition
        r = sr.Recognizer()
        with sr.Microphone() as source:
            print("Speak:")
            audio = r.listen(source)

        try:
            output = " " + r.recognize_google(audio)
        except sr.UnknownValueError:
            # Don't send anything 
            output = "Could not understand audio"
            response_data['flag'] = True
            return HttpResponse(
                json.dumps(response_data),
                content_type="application/json")
        except sr.RequestError as e:
            output = "Could not request results; {0}".format(e)
        data = output
        print(f"{data} is what you said")

        if data is not None:
            # This is a basic logic implementation to get the website working            
            if 'dance' in data:
                random_track = client.get_high_danceability_songs(audio_features)
            elif 'sad' in data:
                random_track = client.get_low_valence_songs(audio_features)
            elif 'happy' in data:
                random_track = client.get_high_valence_songs(audio_features)
            response_data['random_track'] = random_track
            response_data['flag'] = False
            return HttpResponse(
            json.dumps(response_data),
            content_type="application/json")

        response_data['random_track'] = 'https://open.spotify.com/embed/track/2g8HN35AnVGIk7B8yMucww'
        response_data['data'] = data
        response_data['flag'] = False
        return HttpResponse(
            json.dumps(response_data),
            content_type="application/json")
    else:
        return HttpResponse(
            json.dumps({"nothing to see": "this isn't happening"}),
            content_type="application/json" 
        )
