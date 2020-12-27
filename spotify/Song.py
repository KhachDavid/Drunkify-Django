class Song_by(object):
    def __init__(self, valence, track_id, *args, **kwargs):
        """

        :param valence:
        :param track_href:
        :param args:
        :param kwargs:
        """

        # This just help if we want to inherit from other class
        super().__init__(*args, **kwargs)

        self.valence = valence
        self.track_id = track_id

    def get_valence(self):
        return self.valence

    def get_track_id(self):
        return self.track_id

    def compare_to(self, other_song):
        return self.valence - other_song.get_valence()

    def embed_by_id(self):
        return f"https://open.spotify.com/embed/track/{self.track_id}"