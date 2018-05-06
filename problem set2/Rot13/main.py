import webapp2
import cgi

form="""
<form method="post">
    Enter some text to ROT13:
    <br>
    <textarea name="text">
        %(text)s
    </textarea>

    <br>
    <br>
    <input type="submit">
</form>
"""
class MainHandler(webapp2.RequestHandler):

    def escape_text(self, s):
        return cgi.escape(s, quote = True)
        
    def write_form(self, text=""):
        self.response.out.write(form %{"text": text})
    
    def get(self):
        self.write_form()

    def post(self):
        text_str = self.request.get('text')
        text_str_rot13 = ""
        for ch in text_str:
            if (ch==' '):
                text_str_rot13 += ch
            elif ('a'<= ch and ch <= 'z'):
                offset = (ord(ch)-ord('a')+13)%26
                text_str_rot13 += chr(ord('a')+offset)
            elif ('A'<= ch and ch <= 'Z'):
                offset = (ord(ch)-ord('A')+13)%26
                text_str_rot13 += chr(ord('A')+offset)
            else:
                text_str_rot13 += ch
        
        self.write_form(self.escape_text(text_str_rot13))
        
'''
class ThanksHandler(webapp2.RequestHandler):
    def get(self):
        self.response.out.write("Thanks! That's a valid day!")
'''

        
app = webapp2.WSGIApplication([
    ('/', MainHandler),
], debug=True)
