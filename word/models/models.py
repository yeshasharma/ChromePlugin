# -*- coding: utf-8 -*-

from odoo import models, fields, api
import requests
import json


class word(models.Model):
    _name = 'word.word'

    name = fields.Char()
    meaning_ids = fields.One2many('word.meaning','word_id')
    category_ids = fields.Many2many('word.category', 'word_category_rel', 'word_id', 'id')

    @api.multi
    def SearchMeaning(self):
        app_id = 'a60116ea'
        app_key = 'ce012112c8a0b2d424ba457871c7fb00'

        language = 'en'
        # word_id = input('Enter the word:')
        result = self.search([])
        for i in result:
            word = str(i.name)
            url = 'https://od-api.oxforddictionaries.com:443/api/v1/entries/' + language + '/' + word
            r = requests.get(url, headers = {'app_id': app_id, 'app_key': app_key})
            words = {
              'name': i.name,
              'category': [],
              'meaning': []
            }
            if r.status_code == 200:
                data = r.json()
                results = data['results']
            category = self.env['word.category']
            for result in results:
                for lexicalEntry in result['lexicalEntries']:
                    categors = category.search([('name', 'in', [lexicalEntry['lexicalCategory'].lower()])])
                    i.write({'category_ids': [(6, 0, categors.ids)]})
                    for entry in lexicalEntry['entries']:
                        for sense in entry['senses']:
                            words['meaning'].append(sense['definitions'][0])
                            self.env['word.meaning'].create({
                                'name': sense['definitions'][0],
                                'word_id': i.id
                                })


class meaning(models.Model):
    _name = 'word.meaning'

    name = fields.Char()
    word_id = fields.Many2one('word.word', ondelete='cascade', string="word :")


class category(models.Model):
    _name = 'word.category'

    name = fields.Selection([
        ('noun', 'Noun'),
        ('verb', 'Verb'),
        ('adjective', 'Adjective'),
        ('adverb', 'Adverb'),
        ('pronoun', 'Pronoun'),
        ('preposition', 'Preposition'),
        ('conjunction', 'Conjunction')
        ], string='Category')
