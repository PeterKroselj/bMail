#!/usr/bin/env python
import os
import jinja2
import webapp2
import time
import datetime

from models import BMailMsg
from models import BAccount

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
        return self.render_template("bLogin.html")

    def post(self):
        user_name = self.request.get("user_name")
        user_passwd = self.request.get("user_passwd")

        account_list = BAccount.query(BAccount.user_name == user_name).fetch()

        for account in account_list:
            if (user_name == account.user_name) and (user_passwd == account.user_passwd):
                messages = BMailMsg.query(BMailMsg.to_user == user_name).fetch()
                user_id = account.key.id()
                params = {"sent": False, "user_id": user_id, "user_name": user_name, "messages": messages}
                return self.render_template("bmail_browse.html", params=params)

        params = {"ErrorMsg": "Wrong username or password!"}
        return self.render_template("bLogin.html", params=params)

class CreateHandler(BaseHandler):
    def get(self):
        return self.render_template("bCreate.html")

    def post(self):
        user_name = self.request.get("user_name")
        user_passwd_1 = self.request.get("user_passwd_1")
        user_passwd_2 = self.request.get("user_passwd_2")


        if user_name.strip() == "":
            params = {"ErrorMsg": "Enter username!"}
            return self.render_template("bCreate.html", params=params)

        if user_passwd_1.strip() == "":
            params = {"ErrorMsg": "Enter password!"}
            return self.render_template("bCreate.html", params=params)

        if user_passwd_2 <> user_passwd_2:
            params = {"ErrorMsg": "Passwords do not match!"}
            return self.render_template("bCreate.html", params=params)

        account_list = BAccount.query(BAccount.user_name == user_name).fetch()

        for account in account_list:
            if user_name == account.user_name:
                params = {"ErrorMsg": "Username already exists!"}
                return self.render_template("bCreate.html", params=params)

        account = BAccount(user_name=user_name, user_passwd=user_passwd_1)
        account.put()
        return self.redirect_to("login_form")



class EditMsgHandler(BaseHandler):
    def get(self, user_id):
        account = BAccount.get_by_id(int(user_id))
        user_name = account.user_name
        params = {"sent": False, "user_id": user_id, "user_name": user_name}
        return self.render_template("bmail_edit.html", params=params)

    def post(self, user_id):
        account = BAccount.get_by_id(int(user_id))
        from_user = account.user_name
        to_user = self.request.get("to_user")
        msg_text = self.request.get("msg_text")

        msg = BMailMsg(from_user=from_user, to_user=to_user, msg_text=msg_text)
        msg.put()
        time.sleep(0.3)

        messages = BMailMsg.query(BMailMsg.from_user == from_user).fetch()
        params = {"sent": True, "user_id": user_id, "user_name": from_user, "messages": messages}
        return self.render_template("bmail_browse.html", params=params)

class BrowseMsgHandler(BaseHandler):
    def get(self):
        return self.render_template("bmail_browse.html")

class ReceivedMsgHandler(BaseHandler):
    def get(self, user_id):
        account = BAccount.get_by_id(int(user_id))
        user_name = account.user_name
        messages = BMailMsg.query(BMailMsg.to_user == user_name).fetch()
        params = {"sent": False, "user_id": user_id, "user_name": user_name, "messages": messages}
        return self.render_template("bmail_browse.html", params=params)

class SentMsgHandler(BaseHandler):
    def get(self, user_id):
        account = BAccount.get_by_id(int(user_id))
        user_name = account.user_name
        messages = BMailMsg.query(BMailMsg.from_user == user_name).fetch()
        params = {"sent": True, "user_id": user_id, "user_name": user_name, "messages": messages}
        return self.render_template("bmail_browse.html", params=params)


app = webapp2.WSGIApplication([
    webapp2.Route('/', LoginHandler, name="login_form"),
    webapp2.Route('/create', CreateHandler, name="create_form"),
    webapp2.Route('/browse', BrowseMsgHandler, name="browse_msg"),
    webapp2.Route('/edit/<user_id:\d+>', EditMsgHandler, name="edit_msg"),
    webapp2.Route('/received/<user_id:\d+>', ReceivedMsgHandler, name="received_msg"),
    webapp2.Route('/sent/<user_id:\d+>', SentMsgHandler, name="sent_msg"),
], debug=True)
