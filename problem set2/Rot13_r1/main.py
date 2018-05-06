import webapp2
import os
import jinja2



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

class MainHandler(Handler):

    def get(self):
        self.render("rot13.html")
        
    def post(self):
        text = self.request.get("text")
        input = self.rot13(text)
        self.render("rot13.html", input = input)
        

    def rot13(self, input):
        rot13 = ""
        for ch in input:
            if (ch==' '):
                rot13 += ch
            elif ('a'<= ch and ch <= 'z'):
                offset = (ord(ch)-ord('a')+13)%26
                rot13 += chr(ord('a')+offset)
            elif ('A'<= ch and ch <= 'Z'):
                offset = (ord(ch)-ord('A')+13)%26
                rot13 += chr(ord('A')+offset)
            else:
                rot13 += ch
                
        return rot13
        
app = webapp2.WSGIApplication([
    ('/rot13', MainHandler),
], debug=True)