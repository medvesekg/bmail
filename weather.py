from google.appengine.api import urlfetch
import json

class Weather:
    def __init__(self, api_key, location):
        self.target_url = "http://api.openweathermap.org/data/2.5/weather?q="+location+"&units=metric&appid="+api_key
    def get_json(self):
        try:
            data = urlfetch.fetch(self.target_url)
            json_data = json.loads(data.content)
            return json_data
        except:
            return None

    def test(self):
        data = urlfetch.fetch(self.target_url)
        return data.content