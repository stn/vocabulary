# coding:utf-8

import re
from collections import Counter

from db import Word

REF_PAT = re.compile(ur'([a-zA-Z]+)(\d+([-–,]\d+)*)$', re.UNICODE)
WORD_PAT = re.compile(r'[a-zA-Z]+')


class Processor(object):

    def __init__(self):
        self.count_words = 0
        self.count_known_words = 0
        self.count_unknown_words = 0
        self.count_new_words = 0
        self.counter = Counter()
        self.known_words = Word.get_all_known_words()
        self.unknown_words = Word.get_all_unknown_words()

    def process_document(self, document):
        document.title = self.process_text(document.title)
        document.content = self.process_text(document.content)

    def process_text(self, text):
        out = []
        for line in text.splitlines():
            out.append(self.process_line(line))
        return '<br>'.join(out)

    def process_line(self, line):
        out = []
        pre = ''
        suf = ''
        if line.startswith('##### '):
            line = line[6:]
            pre = '<h5>'
            suf = '</h5>'
        elif line.startswith('#### '):
            line = line[5:]
            pre = '<h4>'
            suf = '</h4>'
        elif line.startswith('### '):
            line = line[4:]
            pre = '<h3>'
            suf = '</h3>'
        elif line.startswith('## '):
            line = line[3:]
            pre = '<h2>'
            suf = '</h2>'
        elif line.startswith('# '):
            line = line[2:]
            pre = '<h1>'
            suf = '</h1>'
        for word in re.split(r'[ \t]+', line):
            out.append(self.process_word(word))
        return pre + ' '.join(out) + suf

    def process_word(self, word):
        if len(word) > 1 and word.isalpha():
            self.count_words += 1
            self.counter[word.lower()] += 1
            if word.lower() in self.known_words:
                self.count_known_words += 1
                return self.known_word_link(word, self.known_words[word.lower()])
            elif word.lower() in self.unknown_words:
                self.count_unknown_words += 1
                return self.unknown_word_link(word, self.unknown_words[word.lower()])
            else:
                self.count_new_words += 1
                return self.word_link(word)
        elif word.endswith('.'):
            return self.process_word(word[:-1]) + '.'
        elif word.endswith(','):
            return self.process_word(word[:-1]) + ','
        elif word.endswith(':'):
            return self.process_word(word[:-1]) + ':'
        elif word.endswith(';'):
            return self.process_word(word[:-1]) + ';'
        elif word.endswith('?'):
            return self.process_word(word[:-1]) + '?'
        elif word.endswith('!'):
            return self.process_word(word[:-1]) + '!'
        elif word.startswith('"'):
            return '"' + self.process_word(word[1:])
        elif word.endswith('"'):
            return self.process_word(word[:-1]) + '"'
        elif word.startswith(u'“'):
            return u'“' + self.process_word(word[1:])
        elif word.endswith(u'”'):
            return self.process_word(word[:-1]) + u'”'
        elif word.startswith('('):
            return '(' + self.process_word(word[1:])
        elif word.endswith(')'):
            return self.process_word(word[:-1]) + ')'
        elif word.endswith('\'s'):
            return self.process_word(word[:-2]) + '\'s'
        else:
            m = REF_PAT.search(word)
            if m:
                return self.process_word(m.group(1)) + m.group(2)
            return word

    def word_link(self, word):
        return '<a href="/word?name=' + word.lower() + '" class="new" data-toggle="modal" data-target="#wordModal">' + word + '</a>'

    def known_word_link(self, word, orig):
        return '<a href="/word?name=' + orig + '" class="known" data-toggle="modal" data-target="#wordModal">' + word + '</a>'

    def unknown_word_link(self, word, orig):
        return '<a href="/word?name=' + orig + '" class="unknown" data-toggle="modal" data-target="#wordModal">' + word + '</a>'
