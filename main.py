#!/usr/bin/env python
import os
import cgi
import jinja2
import random
import webapp2
from weather import Weather
from models import Sporocilo
from models import Uporabnik
from google.appengine.api import users


template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape=False)


class BaseHandler(webapp2.RequestHandler):

    def write(self, *a, **kw):
        return self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        return self.write(self.render_str(template, **kw))

    def render_template(self, view_filename, params=None):
        if params is None:
            params = {}
        template = jinja_env.get_template(view_filename)
        return self.response.out.write(template.render(params))


class LoginHandler(BaseHandler):

    def get(self):
        user = users.get_current_user()
        # Check if user is signed in
        if user:
            # If user is not already in database, write user to database
            if not Uporabnik.query(Uporabnik.email == user.email()).fetch():
                uporabnik = Uporabnik(email=user.email())
                uporabnik.put()
            return self.redirect("/home")

        login_url = users.create_login_url("/")
        params = {"login_url": login_url}

        return self.render_template("login.html", params=params)


class MainHandler(BaseHandler):
    def get(self, subpage = "", sporocilo_id = ""):

        #
        #   Global settings
        #

        # Check if user logged in else redirect to login page
        user = users.get_current_user()
        if not user:
            return self.redirect("/")

        # Get weather
        weather = Weather("bd4e6e73d55bd0a7f5b081b6656e05e9", "ljubljana")

        # Set common parameters
        params = {}
        params["logout_url"] = users.create_logout_url("/")
        params["random"] = random.randint(1,8)   # For picking a random ad
        params["weather"] = weather.get_json()



        #
        #   Page specific
        #


        # /home - Main page
        if subpage == "home":
            return self.render_template("home.html", params=params)

        # /prejeto - Inbox
        elif subpage == "prejeto":
            prejeta_sporocila = Sporocilo.query(Sporocilo.to == user.email(), Sporocilo.read == False).fetch()
            prebrana_sporocila = Sporocilo.query(Sporocilo.to == user.email(), Sporocilo.read == True).fetch()
            params["prejeta_sporocila"] = prejeta_sporocila
            params["prebrana_sporocila"] = prebrana_sporocila
            return self.render_template("prejeto.html", params=params)

        # /novo - Send new message form
        elif subpage == "novo":
            params["naslovnik"] = self.request.get("naslovnik")
            params["zadeva"] = self.request.get("zadeva")
            params["sporocilo"] = self.request.get("sporocilo")
            return self.render_template("novo_sporocilo.html", params=params)

        # /poslano - Sent messages
        elif subpage == "poslano":
            poslana_sporocila = Sporocilo.query(Sporocilo.sender == user.email()).fetch(limit=15)
            params["poslana_sporocila"] = poslana_sporocila
            return self.render_template("poslano.html", params=params)

        # /seznam_uporabnikov - List of all users
        elif subpage == "seznam_uporabnikov":
            params["seznam_uporabnikov"] = Uporabnik.query().fetch()
            return self.render_template("seznam_uporabnikov.html", params=params)

        # /javno - Public posts
        elif subpage == "javno":
            javne_objave = Sporocilo.query(Sporocilo.to == "").order(-Sporocilo.nastanek).fetch()
            params["javne_objave"] = javne_objave
            return self.render_template("javne_objave.html", params=params)

        # /sporocilo/<id> - Page for each specific message
        elif subpage == "sporocilo" and sporocilo_id:
            sporocilo = Sporocilo.get_by_id(int(sporocilo_id))
            sporocilo.read = True
            sporocilo.put()
            params["sporocilo"] = sporocilo
            return self.render_template("posamezno_sporocilo.html", params=params)



    def post(self, subpage):

        # Submitting a new message
        if subpage == "novo":
            to = self.request.get("to")
            subject = cgi.escape(self.request.get("subject")).strip()
            vnos = cgi.escape(self.request.get("message")).strip()
            user = users.get_current_user()
            sender = user.email()

            # Make sure required fields are not empty
            if subject == "" or vnos == "":
                return self.redirect("/novo?naslovnik="+to+"&zadeva="+subject+"&sporocilo="+vnos)

            sporocilo = Sporocilo(vnos=vnos, sender=sender, to=to, subject=subject)
            sporocilo.put()
            self.redirect("/poslano")



class WeatherHandler(BaseHandler):
    def get(self):
        return self.write("ha")
    def post(self):
        #location = self.request.get("location")
        weather = Weather("bd4e6e73d55bd0a7f5b081b6656e05e9", self.request.get("location"))
        return self.write(weather.test())



app = webapp2.WSGIApplication([
    webapp2.Route('/', LoginHandler),
    webapp2.Route('/weather', WeatherHandler),
    webapp2.Route('/<subpage>', MainHandler),
    webapp2.Route('/<subpage>/<sporocilo_id:\d+>', MainHandler),
], debug=True)
