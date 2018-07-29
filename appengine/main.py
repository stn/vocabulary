# coding:utf-8

# !/usr/bin/env python

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

from collections import defaultdict
import csv
from datetime import datetime
import json
import os
import re
import StringIO

import jinja2
import webapp2

from process import Processor
from db import Document, Word, Collocation

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
        processor = Processor()
        processor.process_document(document)
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


class DeleteDocumentHandler(webapp2.RequestHandler):

    def post(self):
        id = self.request.get('id')
        if id == '':
            # Error
            self.redirect('/')
            return

        document = Document.get_with_namespace(int(id))
        if document is None:
            # Error
            self.redirect('/')
            return

        document.key.delete()
        self.redirect('/')


class WordHandler(webapp2.RequestHandler):

    def get(self):
        word_name = self.request.get('name')
        if word_name == '':
            self.redirect('/')
            return

        word = Word.get_by_name_or_new_with_namespace(word_name)
        template_values = {
            'word': word,
        }
        template = JINJA_ENVIRONMENT.get_template('word.html')
        self.response.write(template.render(template_values))

    def post(self):
        word_name = self.request.get('name')
        if word_name == '':
            payload = {'success': False}
            return self.response.write(json.dumps(payload))
        word_name = word_name.lower()

        word = Word.get_by_name_or_new_with_namespace(word_name)
        word.conjugative = self.request.get('conjugative').split()
        word.content = self.request.get('content')
        word.known = self.request.get('known') == 'known'
        Word.put_with_namespace(word)
        payload = {'success': True}
        return self.response.write(json.dumps(payload))


class DeleteWordHandler(webapp2.RequestHandler):

    def post(self):
        word_name = self.request.get('name')
        if word_name == '':
            payload = {'success': False}
            return self.response.write(json.dumps(payload))
        word_name = word_name.lower()

        word = Word.get_by_name_or_new_with_namespace(word_name)
        if word is None:
            payload = {'success': False}
            return self.response.write(json.dumps(payload))
        word.key.delete()
        payload = {'success': True}
        return self.response.write(json.dumps(payload))


class ListWordsHandler(webapp2.RequestHandler):

    def get(self):
        words = Word.get_all_words()
        words = sorted(words, key=lambda w: w.name)

        count_known = 0
        count_unknown = 0
        for word in words:
            if word.known:
                count_known += 1
            else:
                count_unknown += 1

        template_values = {
            'words': words,
            'count_known': count_known,
            'count_unknown': count_unknown,
        }

        template = JINJA_ENVIRONMENT.get_template('words.html')
        self.response.write(template.render(template_values))


class BackupWordsHandler(webapp2.RequestHandler):

    def get(self):
        self.response.headers['Content-Type'] = 'application/json; charset=utf-8'
        self.response.headers['Content-Disposition'] = 'attachment; filename=backup_words.json'

        words = Word.get_all_words()
        words = sorted(words, key=lambda w: w.name)

        for word in words:
            obj = {}
            obj['name'] = word.name
            obj['conjugative'] = [conj for conj in word.conjugative]
            obj['content'] = word.content
            obj['known'] = word.known
            obj['date'] = word.date.strftime("%Y/%m/%d %H:%M:%S")
            self.response.out.write(json.dumps(obj, ensure_ascii=False).encode('utf-8'))
            self.response.out.write('\n')


class RestoreWordsHandler(webapp2.RequestHandler):

    def post(self):
        reader = StringIO.StringIO(self.request.get('json'))
        words = []
        for row in reader:
            obj = json.loads(row)
            self.response.out.write(obj['name'])
            self.response.out.write('<br>')
            word = Word.get_by_name_or_new_with_namespace(obj['name'])
            word.conjugative = obj['conjugative']
            word.content = obj['content']
            word.known = obj['known']
            word.date = datetime.strptime(obj['date'], '%Y/%m/%d %H:%M:%S')
            words.append(word)
        Word.put_multi_with_namespace(words)


class UpdateCollocationHandler(webapp2.RequestHandler):

    def get(self):
        documents = Document.get_all_with_namespace()
        text = ''
        for document in documents:
            collocations = defaultdict(list)
            text = re.sub(r'[\r\n]', ' ', document.content)
            collocations = Processor.build_collocation(text, collocations)

        colls = []
        for k, v in collocations.items():
            coll = Collocation.get_by_name_or_new_with_namespace(k)
            coll.collocation = '\n'.join(v)
            colls.append(coll)
        Collocation.put_multi_with_namespace(colls)

        payload = {'success': True}
        return self.response.write(json.dumps(payload))


app = webapp2.WSGIApplication([
    ('/', MainPageHandler),
    ('/doc/(\d+)', ShowDocumentHandler),
    ('/doc/new', EditDocumentHandler),
    ('/doc/edit', EditDocumentHandler),
    ('/doc/save', EditDocumentHandler),
    ('/doc/delete', DeleteDocumentHandler),
    ('/word', WordHandler),
    ('/word/delete', DeleteWordHandler),
    ('/words', ListWordsHandler),
    ('/words/backup', BackupWordsHandler),
    ('/words/restore', RestoreWordsHandler),
    ('/collocation/update', UpdateCollocationHandler),
], debug=True)
