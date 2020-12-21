import base64
import datetime
from urllib.parse import urlencode, quote
import requests
from musicplayer.models import Song
from .quick_sort import quick_sort
import random


class SpotifyAPI(object):
    # This variable gives access to the API
    access_token = None

    access_token_expires = datetime.datetime.now()
    client_id = None
    client_secret = None
    access_token_did_expire = True

    token_url = 'https://accounts.spotify.com/api/token'
    SPOTIFY_API_BASE_URL = "https://api.spotify.com"
    API_VERSION = "v1"
    SPOTIFY_API_URL = "{}/{}".format(SPOTIFY_API_BASE_URL, API_VERSION)

    scope = "playlist-modify-public playlist-modify-private"
    state = ""
    show_dialog_bool = True
    show_dialog_str = str(show_dialog_bool).lower()

    def __init__(self, client_id, client_secret, show_dialog_bool=True,
                 show_no_spotify_dialog_bool=True, *args, **kwargs):
        """
        Constructor Method for the API
        Creates an object using developer account details
        https://developer.spotify.com/dashboard/applications/fb1324d95b384e17a6e4838f3ab7cfb8
        :param client_id: found in the link above
        :param client_secret: found in the link above
        :param args:
        :param kwargs:
        """

        # This just help if we want to inherit from other class
        super().__init__(*args, **kwargs)

        # Initialize values
        self.client_id = client_id
        self.client_secret = client_secret
        self.show_dialog_bool = show_dialog_bool
        self.show_no_spotify_dialog_bool = show_no_spotify_dialog_bool
        SPOTIFY_API_BASE_URL = "https://api.spotify.com"
        API_VERSION = "v1"
        self.SPOTIFY_API_URL = "{}/{}".format(SPOTIFY_API_BASE_URL, API_VERSION)

    def get_client_credentials(self):
        """
        :return: a base 64 encoded string
        """

        if self.client_secret is None or self.client_id is None:
            raise Exception("You must set client_id or client_secret")

        # client credits must be a base 64 encoded string
        # as per by the documentation of Spotify API
        client_creds = f"{self.client_id}:{self.client_secret}"
        client_creds_b64 = base64.b64encode(client_creds.encode())

        return client_creds_b64.decode()

    def get_token_header(self):
        """
        :return: the token header
        """
        client_creds_b64 = self.get_client_credentials()
        return {
            "Authorization": f"Basic {client_creds_b64}"
        }

    def get_token_data(self):
        """
        Specified by the Spotify API documentation
        :return: the token data
        """
        return {
            "grant_type": "client_credentials"
        }

    def get_token_url(self):
        return self.token_url

    def perform_auth(self):
        """
        This function extracts the access token
        :return: True if successful, raise Exception if unsuccessful
        """

        # Makes an API request
        # Uses the data and the header as per by the documentation
        r = requests.post(self.token_url, data=self.get_token_data(), headers=self.get_token_header())

        # in case the response is not okay
        if r.status_code not in range(200, 299):
            raise Exception('Failed to Authenticate')

        # Jsonify the token data
        data = r.json()

        now = datetime.datetime.now()
        access_token = data['access_token']
        expires_in = data['expires_in']

        # Set the expiration time
        # The moment token was generated + the time it will take to expire
        expires = now + datetime.timedelta(seconds=expires_in)

        # Reinitialize class variables
        self.access_token = access_token
        self.access_token_expires = expires
        self.access_token_did_expire = expires < now
        return True

    def get_access_token(self):
        """
        A recursive function that returns the access token itself
        It also prevents the token from expiring
        Once the token is expired, the function will call perform_auth() to reset the token
        :return: the access token
        """
        token = self.access_token
        expires = self.access_token_expires
        now = datetime.datetime.now()

        if expires < now:
            self.perform_auth()
            return self.get_access_token()

        elif token is None:
            self.perform_auth()
            return self.get_access_token()

        return token

    def get_headers(self):
        """
        :return: the header with the token of type bearer
        """

        access_token = self.get_access_token()
        return {
            "Authorization": f"Bearer {access_token}"
        }

    def base_search(self, query_params):
        """
        Makes the final query
        The syntax of function calls is specified in the Spotify API documentation
        :param query_params: The complete query to execute
        :return: A JSON object containing the search results
        """

        # Extract the access token
        headers = self.get_headers()

        endpoint = 'https://api.spotify.com/v1/search'
        lookup_url = f"{endpoint}?{query_params}"

        # Make the API request
        r = requests.get(lookup_url, headers=headers)

        if r.status_code not in range(200, 299):
            return {}

        # Return the results
        return r.json()

    def search(self, query=None, search_type='playlist'):
        """
        Converts the query to a list and creates another dictionary to
        execute a query using the search type and the query itself
        :param query: By default is a list containing the query
        :param search_type: By default is a playlist
        :return: The a JSON object extracted from a base search using a query
        """
        if query is None:
            raise Exception("Query Is Required")

        if isinstance(query, dict):
            # convert dictionary to a list
            query = " ".join([f"{k}:{v}" for k, v in query.items()])

        query_params = urlencode({"q": query, "type": search_type.lower()})
        return self.base_search(query_params)

    def get_resource(self, lookup_id, resource_type='albums', version='v1'):
        """
        Gets a given resource by id
        :param lookup_id:
        :param resource_type:
        :param version: By default is 'v1' as per by the Spotify documentation
        :return:
        """

        # https://api.spotify.com/v1/albums/189237827
        endpoint = f"https://api.spotify.com/{version}/{resource_type}/{lookup_id}"

        # contains the access token
        # must be in the API request call
        headers = self.get_headers()

        r = requests.get(endpoint, headers=headers)

        if r.status_code not in range(200, 299):
            return {}

        return r.json()

    def get_album(self, _id):
        """
        :param _id: Is an id of an album
        :return: A JSON object containing the results of searching by id
        """
        return self.get_resource(_id)

    def get_artist(self, _id):
        """
        :param _id:  Is an id of an artist
        :return: A JSON object containing the results of searching by id
        """
        return self.get_resource(_id, resource_type='artists')

    # Refresh Token
    def get_show_dialog(self):
        """
        True - if the user has to give access everything signing in with Spotify
        False - if the user has to give access once
        :return:
        """
        return self.show_dialog_bool

    def set_show_dialog_false(self):
        self.show_dialog_bool = False

    def set_show_dialog_true(self):
        self.show_dialog_bool = True

    def get_auth_query(self):
        auth_query_parameters = {
            "response_type": "code",
            "redirect_uri": "http://127.0.0.1:5000/callback",
            "scope": "playlist-modify-public playlist-modify-private",
            "state": "",
            "show_dialog": str(self.get_show_dialog()).lower(),
            "client_id": self.client_id
        }

        return auth_query_parameters

    def get_authentication_url(self):
        return "https://accounts.spotify.com/authorize"

    def generate_auth_url(self):
        url_args = "&".join(["{}={}".format(key, quote(val)) for key, val in self.get_auth_query().items()])
        auth_url = "{}/?{}".format(self.get_authentication_url(), url_args)
        print(12289739837)
        return auth_url

    def set_no_spotify_dialog_true(self):
        self.show_no_spotify_dialog_bool = True

    def set_no_spotify_dialog_false(self):
        self.show_no_spotify_dialog_bool = False

    def get_no_spotify_dialog(self):
        return self.show_no_spotify_dialog_bool

    def get_users_top(self, auth_header, t):
        if t not in ['artists', 'tracks']:
            print('invalid type')
            return None
        url = 'https://api.spotify.com/v1/me/top/tracks?limit=' + '50' + '&time_range=' + 'medium_term'
        r_tt = requests.get(url, headers=auth_header)
        tt_json = r_tt.json()
        track_list = []
        track_ids = []

        for x in range(0, tt_json['limit']):
            track_name = tt_json['items'][x]['name']
            track_id = tt_json['items'][x]['id']
            track_album = tt_json['items'][x]['album']['name']
            track_artist = tt_json['items'][x]['artists'][0]['name']

            track = {'name': track_name,
                     'artist': track_artist,
                     'album': track_album,
                     'id': track_id}

            track_list.append(track)
            track_ids.append(track_id)

        return track_list, track_ids

    def get_audio_features(self, auth_header, track_ids):  # track_ids = list of track ids
        GET_AUDIOFEAT_ENDPOINT = "{}/{}".format(self.SPOTIFY_API_URL, 'audio-features/?ids=')  # /<track id>

        url = GET_AUDIOFEAT_ENDPOINT  # generate URL to query track ids
        for i in range(len(track_ids)):
            url = url + track_ids[i] + ','

        r_tt = requests.get(url, headers=auth_header)  # Get JSON of each track's audio features
        return r_tt.json()

    def embedify(self, random_track):
        x = random_track.split("/")
        random_track = x[0] + "//" + x[2] + "/embed/" + x[3] + "/" + x[4]  # Adding the embed parameter to send through
        # jinja
        return random_track

    def get_low_valence_songs(self, audio_features):
        tracks = []
        for i in range(len(audio_features['audio_features'])):
            new_song = Song(audio_features['audio_features'][i]['valence'],
                            audio_features['audio_features'][i]['id'])
            tracks.append(new_song)
        quick_sort(tracks, 0, len(tracks) - 1)

        if len(tracks) / 4 == 0:
            n = random.randint(0, 1)
            return tracks[n].embed_by_id()
        n = random.randint(0, int(len(tracks) / 4))
        print(tracks[n].valence)
        return tracks[n].embed_by_id()

    def get_high_valence_songs(self, audio_features):
        tracks = []
        for i in range(len(audio_features['audio_features'])):
            new_song = Song(audio_features['audio_features'][i]['valence'],
                            audio_features['audio_features'][i]['id'])
            tracks.append(new_song)
        quick_sort(tracks, 0, len(tracks) - 1)
        n = random.randint(int(len(tracks) * 3 / 4), int(len(tracks) - 1))
        print(tracks[n].valence)
        return tracks[n].embed_by_id()