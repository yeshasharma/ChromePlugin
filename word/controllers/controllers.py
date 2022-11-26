# -*- coding: utf-8 -*-
from odoo import http
import odoo
from odoo.http import request
import requests
import json


class Word(http.Controller):
    @http.route('/word/word/', auth='public', website=True)
    def index(self, **kw):
        return http.request.render('word.index')

    @http.route('/word/word/meaning', type="http", auth='public', website=True, csrf=False)
    def search_meaning(self, word, **kw):
        print(kw)
        Words = http.request.env['word.word'].search([('name', '=', word)])
        wordid = Words.id
        print("ID", wordid)
        print("YYYY", Words.meaning_ids, Words.category_ids)

        cat = []
        for category in Words.category_ids:
            cat.append(category.name)
            print("Category", cat)

        mean = []
        for meaning in Words.meaning_ids:
            mean.append(meaning.name)
            print("Meaning", mean)
        return http.request.render('word.index', {
            'results': Words.search([('name', '=', word)]),
            'meanings': mean,
            'categories': cat
            })

    @http.route('/word/test_pdf/', type="http", auth='public', website=True)
    def test(self, **kw):
        pdf = open(odoo.modules.module.get_resource_path('word', 'test.pdf'), 'rb')
        pdfread = pdf.read()
        pdfhttpheaders = [
            ('Content-Type', 'application/pdf'),
            ('Content-Length', len(pdfread)),
        ]
        return request.make_response(pdfread, headers=pdfhttpheaders)

    @http.route('/word/meaning', type='json', auth='public', website=True, csrf=False)
    def get_meaning(self, **kw):
        print("the value of kw", kw)
        word = kw['name']
        print("Word", word)
        Words = http.request.env['word.word'].search([('name', '=', word)])
        if Words:
            name = Words.name
        else:
            print(word)
            app_id = 'a60116ea'
            app_key = 'ce012112c8a0b2d424ba457871c7fb00'

            language = 'en'
            word = str(word)
            url = 'https://od-api.oxforddictionaries.com:443/api/v1/entries/' + language + '/' + word
            r = requests.get(url, headers={'app_id': app_id, 'app_key': app_key})
            words = {
              'name': word,
              'category': [],
              'meaning': []
                }
            if r.status_code == 200:
                data = r.json()
                results = data['results']
                category = http.request.env['word.category']
                for result in results:
                    for lexicalEntry in result['lexicalEntries']:
                        categors = category.search([('name', 'in', [lexicalEntry['lexicalCategory'].lower()])])
                        self.write({'category_ids': [(6, 0, categors.ids)]})
                        for entry in lexicalEntry['entries']:
                            for sense in entry['senses']:
                                words['meaning'].append(sense['definitions'][0])
                                http.request.env['word.meaning'].create({
                                    'name': sense['definitions'][0],
                                    'word_id': self.id
                                    })

        wordid = Words.id
        print("ID", wordid)
        print("YYYY", Words.meaning_ids, Words.category_ids)

        cat = []
        for category in Words.category_ids:
            cat.append(category.name)
            print("Category", cat)

        name = ""
        mean = []
        for meaning in Words.meaning_ids:
            mean.append(meaning.name)
            print("Meaning", mean)
            name = Words.search([('name', '=', word)])

            return {
                'word': name,
                'meanings': mean,
                'categories': cat
            }
