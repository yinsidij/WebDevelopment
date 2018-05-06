import webapp2
import re

form="""
<form method="post">
    Signup
    <br>
    <label>
        Username<input type="text" name="userName"><div style="color: red">%(userNameErr)s</div>
    </label>
    <label>
        Password<input type="password" name="passWord0"><div style="color: red">%(passWord0Err)s</div>
    </label>
    <label>
        Verify Password<input type="password" name="passWord1"><div style="color: red">%(passWord1Err)s</div>
    </label>
    <label>
        Email(optional)<input type="text" name="email"><div style="color: red">%(emailErr)s</div>
    </label>

    <br>
    <input type="submit">
</form>
"""

form_welcome="""
<form>
    Welcome, %(userName)s
</form>


"""

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
    
class MainHandler(webapp2.RequestHandler):

    
    def write_form(self, userNameErr="", passWord0Err="", passWord1Err="", emailErr=""):
        self.response.out.write(form %{"userNameErr":   userNameErr, 
                                        "passWord0Err": passWord0Err, 
                                        "passWord1Err": passWord1Err, 
                                        "emailErr": emailErr})
    
    def get(self):
        self.write_form()

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
                self.write_form("That's not a valid username. ", "", "Your passwords didn't match. ", ("" if isValidEmail(user_email) else "That's not a valid email. "))
            elif not user_isValidPassWord:
                self.write_form("That's not a valid username. ", "That wasn't a valid password. ", "", ("" if isValidEmail(user_email) else "That's not a valid email. "))
            else:
                self.write_form("That's not a valid username. ", "", "", ("" if isValidEmail(user_email) else "That's not a valid email. "))
        else:
            if not user_isMatchedPassWord:
                self.write_form("", "", "Your passwords didn't match. ", ("" if isValidEmail(user_email) else "That's not a valid email. "))
            elif not user_isValidPassWord:
                self.write_form("", "That wasn't a valid password. ", "", ("" if isValidEmail(user_email) else "That's not a valid email. "))            
            else:
                self.redirect('/welcome?username=' + user_userName)


            
class WelcomeHandler(webapp2.RequestHandler):
    def get(self):
        username = self.request.get('username')
        self.response.out.write(form_welcome %{"userName": username})
        
app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/welcome', WelcomeHandler)
], debug=True)
