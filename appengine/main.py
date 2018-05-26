# coding:utf-8

#!/usr/bin/env python

# Copyright 2018 Akira Ishino.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os

import jinja2
import webapp2

from db import Document

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


class MainPageHandler(webapp2.RequestHandler):

    def get(self):
        documents = Document.get_all_with_namespace()
        template_values = {
            'documents': documents,
        }
        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values))


class ShowDocumentHandler(webapp2.RequestHandler):

    def get(self, *args):
        id = args[0]
        document = Document.get_with_namespace(int(id))
        template_values = {
            'document': document,
        }
        template = JINJA_ENVIRONMENT.get_template('document_show.html')
        self.response.write(template.render(template_values))


class EditDocumentHandler(webapp2.RequestHandler):

    def get(self):
        id = self.request.get('id')
        if id == '':
            document = Document.new()
        else:
            document = Document.get_with_namespace(int(id))
        template_values = {
            'document': document,
        }
        template = JINJA_ENVIRONMENT.get_template('document_edit.html')
        self.response.write(template.render(template_values))

    def post(self):
        id = self.request.get('id')
        if id == '':
            document = Document.new()
        else:
            document = Document.get_with_namespace(int(id))
        document.title = self.request.get('title')
        document.content = self.request.get('content')
        Document.put_with_namespace(document)
        self.redirect('/')


app = webapp2.WSGIApplication([
    ('/', MainPageHandler),
    ('/doc/(\d+)', ShowDocumentHandler),
    ('/doc/new', EditDocumentHandler),
    ('/doc/edit', EditDocumentHandler),
    ('/doc/save', EditDocumentHandler),
], debug=True)
