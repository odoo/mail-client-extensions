# -*- coding: utf-8 -*-
from contextlib import closing
from lxml import etree
from openerp.tools import file_open

def migrate(cr, version):
    with closing(file_open('addons/base/res/res_currency_data.xml')) as fp:
        tree = etree.parse(fp)
        currencies = [node.get('id') for node in tree.xpath('//record[@model="res.currency"]')]
    cr.execute("""
        INSERT INTO ir_model_data(module, name, model, res_id, noupdate)
             SELECT 'base', name, 'res.currency', id, true
               FROM res_currency c
              WHERE name = ANY(%s)
                AND NOT EXISTS(SELECT 1
                                 FROM ir_model_data
                                WHERE model='res.currency'
                                  AND name=c.name)
    """, [currencies])
