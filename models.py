from google.appengine.ext import ndb

class Sporocilo(ndb.Model):
    vnos = ndb.StringProperty()
    sender = ndb.StringProperty()
    to = ndb.StringProperty()
    subject = ndb.StringProperty()
    nastanek = ndb.DateTimeProperty(auto_now_add=True)
    deleted = ndb.BooleanProperty(default=False)
    read = ndb.BooleanProperty(default=False)

class Uporabnik(ndb.Model):
    email = ndb.StringProperty()
