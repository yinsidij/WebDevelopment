import webapp2
import os
import jinja2

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

class Blog(db.Model):
    subject = db.StringProperty(required = True)
    blog = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class NewPost(Handler):
    def render_newpost(self, subject="", blog="", error=""):
        self.render("new_post.html", subject=subject, blog=blog, error=error)
    
    def get(self):
        self.render_newpost()
        
    def post(self):
        subject = self.request.get("subject")
        blog = self.request.get("blog")
        
        if subject and blog:
            b = Blog(subject = subject, blog = blog)
            b.put()
            
            post_id = str(b.key().id())
            self.redirect("/blog/"+post_id)
        else:
            error = "we need both a subject and blog!"
            self.render_newpost(subject = subject, blog = blog, error = error)
            
class MainPage(Handler):
    
    def render_front(self):
        blogs = db.GqlQuery("SELECT * FROM Blog ORDER BY created DESC")
                        
        self.render("main.html", blogs=blogs)
        
    def get(self):
        self.render_front()
    
    def post(self):
        self.render_front()
            
class BlogPage(Handler):
    def get(self, post_id):
        b = Blog.get_by_id(int(post_id))
        if b:
            self.render("main.html", blogs=[b])
        


        
app = webapp2.WSGIApplication([
    ('/blog', MainPage),
    ('/blog/newpost', NewPost),
    ('/blog/(\d+)', BlogPage)
], debug=True)
