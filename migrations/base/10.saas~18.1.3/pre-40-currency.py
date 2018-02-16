# -*- coding: utf-8 -*-
from contextlib import closing

from lxml import etree

from odoo.addons.base.maintenance.migrations import util
from odoo.tools import file_open

class NULL:
    text = None

def migrate(cr, version):
    util.create_column(cr, 'res_currency', 'currency_unit_label', 'varchar')
    util.create_column(cr, 'res_currency', 'currency_subunit_label', 'varchar')

    labels = []
    with closing(file_open('addons/base/res/res_currency_data.xml')) as fp:
        tree = etree.parse(fp)
        for node in tree.xpath('//record[@model="res.currency"]'):
            labels.append((
                (node.findall('field[@name="currency_unit_label"]') or [NULL])[0].text,     # ^0
                (node.findall('field[@name="currency_subunit_label"]') or [NULL])[0].text,
                node.get('id'),
            ))

    cr.executemany("""
        UPDATE res_currency
           SET currency_unit_label=%s,
               currency_subunit_label=%s
         WHERE id = (SELECT res_id
                       FROM ir_model_data
                      WHERE model='res.currency'
                        AND module='base'
                        AND name=%s)
    """, labels)


# XXX ^0: As `__bool__` on lxml.Element only check if the element has children (__len__), we need
#         to call `findall()` to get a `list` that can be converted to bool without ambiguities.
