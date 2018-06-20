from google.appengine.ext import ndb

class BMailMsg(ndb.Model):
    from_user = ndb.StringProperty()
    to_user = ndb.StringProperty()
    msg_text = ndb.StringProperty()
    sent_date = ndb.DateTimeProperty(auto_now_add=True)

class BAccount(ndb.Model):
    user_name = ndb.StringProperty()
    user_passwd = ndb.StringProperty()
    created = ndb.DateTimeProperty(auto_now_add=True)