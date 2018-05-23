import string

from google.appengine.api import namespace_manager
from google.appengine.api import users
from google.appengine.ext import ndb

NAMESPACE_TRANS = string.maketrans("!@#$%&'*+/=?^`{|}~", "------------------")


class Word(ndb.Model):
    """A model for representing a word."""
    name = ndb.StringProperty()
    conjugative = ndb.StringProperty(repeated=True)
    content = ndb.TextProperty()
    known = ndb.BooleanProperty()
    date = ndb.DateTimeProperty(auto_now_add=True)


class Document(ndb.Model):
    """A main model for representing an individual Note entry."""
    title = ndb.StringProperty(indexed=False)
    content = ndb.TextProperty(indexed=False)
    date = ndb.DateTimeProperty(auto_now_add=True)

    @classmethod
    def new(cls):
        user = users.get_current_user()
        previous_namespace = namespace_manager.get_namespace()
        try:
            namespace_manager.set_namespace(user.email().translate(NAMESPACE_TRANS))
            document = Document()
        finally:
            namespace_manager.set_namespace(previous_namespace)
        document.title = ''
        document.content = ''
        return document

    @classmethod
    def get_all_with_namespace(cls):
        user = users.get_current_user()
        previous_namespace = namespace_manager.get_namespace()
        try:
            namespace_manager.set_namespace(user.email().translate(NAMESPACE_TRANS))
            documents_query = Document.query().order(-Document.date)
            documents = documents_query.fetch()
        finally:
            namespace_manager.set_namespace(previous_namespace)
        return documents

    @classmethod
    def get_with_namespace(cls, id):
        user = users.get_current_user()
        previous_namespace = namespace_manager.get_namespace()
        try:
            namespace_manager.set_namespace(user.email().translate(NAMESPACE_TRANS))
            document = Document.get_by_id(id)
        finally:
            namespace_manager.set_namespace(previous_namespace)
        return document

    @classmethod
    def put_with_namespace(cls, document):
        user = users.get_current_user()
        previous_namespace = namespace_manager.get_namespace()
        try:
            namespace_manager.set_namespace(user.email().translate(NAMESPACE_TRANS))
            document.put()
        finally:
            namespace_manager.set_namespace(previous_namespace)


class Collocation(ndb.Model):
    """A model for representing a collocation."""
    name = ndb.StringProperty()
    collocation = ndb.TextProperty()
    date = ndb.DateTimeProperty(auto_now_add=True)
