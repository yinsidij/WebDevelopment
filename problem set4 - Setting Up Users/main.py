import webapp2
import os
import jinja2
import datetime
import re
import hashlib
import logging

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)
        
    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)
        
    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    def initialize(self, *a, **kw):
        webapp2.RequestHandler.initialize(self, *a, **kw)
        cookie_val = self.request.cookies.get("user_id", 'path=/')
        logging.info("Handler initializing stars...")
        id = check_cookie(cookie_val)
        logging.info(id)
        if id:
            
            self.r = Registration.getEntryById(id)
            logging.info(self.r.user)
        else:
            self.r = None
            
        logging.info("Handler initializing ends...")
#Database        
class Registration(db.Model):
    user = db.StringProperty(required = True)
    pw = db.StringProperty(required = False)
    email = db.StringProperty(required = False)
    created = db.DateTimeProperty(auto_now_add = True)

    @classmethod
    def containsId(cls, id):
        return Registration.get_by_id(id) != None

    @classmethod
    def containsUser(cls, user):
        logging.info("trying to receive user")
        r = Registration.all().filter('user =', user).get()
        return r != None
        
    @classmethod
    def getEntryById(cls, id):
        r = Registration.get_by_id(int(id))
        return r    
        
    @classmethod
    def getEntryByUser(cls, user):
        r = Registration.all().filter('user =', user).get()
        return r        
        
#Following code reused codes in Lesson 2
USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
def isValidUserName(userName):
    return USER_RE.match(userName)

PW_RE = re.compile(r"^.{3,20}$")
def isValidPassWord(userInput):
    return PW_RE.match(userInput)
    
EMAIL_RE = re.compile("^[\S]+@[\S]+.[\S]+$")
def isValidEmail(userEmail):
    if (userEmail == ""):
        return True
    return EMAIL_RE.match(userEmail)

#For cookie
def hash_str(id):
    return hashlib.md5(id).hexdigest()
    
def make_cookie(id):
    return "%s|%s" % (id, hash_str(id))

def check_cookie(h):
    val = h.split('|')[0]
    if h==make_cookie(val):
        return val
    return None

#For password in db    
def hash_pw(s):
    return hashlib.md5(s).hexdigest()
    
def is_valid_pw(pw, h):
    return hashlib.md5(pw).hexdigest() == h
    

class Welcome(Handler):
    def get(self):
        cookie_str = self.request.cookies.get('user_id')
        logging.info(cookie_str)
        if cookie_str:
            cookie_val = check_cookie(cookie_str)
            if cookie_val:
                self.render("welcome.html", userName=self.r.user)
            else:
                self.redirect('/blog/signup')
        else:
            self.redirect('/blog/signup')

class Signup(Handler):
    def render_signup(self, userNameErr="", passWord0Err="", passWord1Err="", emailErr=""):
        self.render("signup.html", userNameErr=userNameErr, passWord0Err=passWord0Err, passWord1Err=passWord1Err, emailErr=emailErr)

        
    def get(self):
        self.render_signup()
        
    def post(self):
        user_userName = self.request.get('userName')
        user_passWord0= self.request.get('passWord0')
        user_passWord1= self.request.get('passWord1')
        user_email = self.request.get('email')
        
        user_isValidUserName = True 
        user_isMatchedPassWord = True
        user_isValidPassWord = True
        
        if not isValidUserName(user_userName):
            user_isValidUserName = False
        
        if not (user_passWord0 == user_passWord1):
            user_isMatchedPassWord = False
        elif not (isValidPassWord(user_passWord0)):
            user_isValidPassWord = False
            
            
        if not user_isValidUserName:
            if not user_isMatchedPassWord:
                self.render_signup("That's not a valid username. ", "", "Your passwords didn't match. ", ("" if isValidEmail(user_email) else "That's not a valid email. "))
            elif not user_isValidPassWord:
                self.render_signup("That's not a valid username. ", "That wasn't a valid password. ", "", ("" if isValidEmail(user_email) else "That's not a valid email. "))
            else:
                self.render_signup("That's not a valid username. ", "", "", ("" if isValidEmail(user_email) else "That's not a valid email. "))
        else:
            if not user_isMatchedPassWord:
                self.render_signup("", "", "Your passwords didn't match. ", ("" if isValidEmail(user_email) else "That's not a valid email. "))
            elif not user_isValidPassWord:
                self.render_signup("", "That wasn't a valid password. ", "", ("" if isValidEmail(user_email) else "That's not a valid email. "))            
            else:
                #userName and passwords look good
                #check whether it is the existing user
                #if yes, show error message
                #if no, do 
                if (Registration.containsUser(user_userName)):
                    self.render_signup("This user existed", "", "", "")
                else:
                    r = Registration(user = user_userName, pw=hash_pw(user_passWord0), email = user_email)
                    r.put()
                    cookie_val = make_cookie(str(r.key().id()))
                    self.response.headers.add_header('Set-Cookie', 'user_id=%s; Path=/' %cookie_val)
                    self.redirect('/blog/welcome')

            
class MainPage(Handler):
    def get(self):
        self.redirect('/blog/signup')
            
class Login(Handler):
    def render_login(self, userNameErr="", passWordErr=""):
        self.render("login.html", userNameErr=userNameErr, passWordErr=passWordErr)
        
    def get(self):
        self.render_login()
        
    def post(self):
        user_userName = self.request.get('userName')
        user_passWord = self.request.get('passWord')
        r = Registration.getEntryByUser(user_userName)
        if r:
            #found in database
            logging.info("found in database")
            if is_valid_pw(user_passWord, r.pw):
                #password matches, direct to welcome
                logging.info("password correct")
                logging.info(r.user)
                cookie_val = make_cookie(str(r.key().id()))
                self.response.headers.add_header('Set-Cookie', 'user_id=%s path=/' %cookie_val)
                self.redirect('/blog/welcome')
            else:
                logging.info("password incorrect")
                #password doesn't match
                self.render("login.html", passWordErr="Password doesn't match")
        else:
            self.render("login.html", userNameErr="This user doesn't exist")

        
class Logout(Handler):
    def get(self):
        self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')
        self.redirect('/blog')


app = webapp2.WSGIApplication([
    ('/blog', MainPage),
    ('/blog/signup', Signup),
    ('/blog/login', Login),
    ('/blog/logout', Logout),
    ('/blog/welcome', Welcome)
], debug=True)