# -*- coding: utf-8 -*-
from ast import literal_eval
from collections import defaultdict
from contextlib import closing

from lxml import etree

from odoo.addons.base.maintenance.migrations import util
from odoo.tools import file_open

def migrate(cr, version):
    used_counties = ' UNION '.join(
        'SELECT {1} AS id FROM {0} WHERE {1} IS NOT NULL'.format(tbl, col)
        for tbl, col, _, _ in util.get_fk(cr, 'res_country')
    )
    cr.execute("""
        DELETE FROM res_country
              WHERE code IN ('an', 'nt', 'tp', 'yu', 'zr')
                AND id NOT IN ({})
    """.format(used_counties))
    cr.execute("""
        DELETE FROM ir_model_data
              WHERE model = 'res.country'
                AND res_id NOT IN (SELECT id FROM res_country)
    """)

    util.create_column(cr, 'res_country', 'vat_label', 'varchar')

    value_for = {
        # field: [(value, [xids])]
    }

    with closing(file_open('addons/base/res/res_country_data.xml')) as fp:
        tree = etree.parse(fp)
        vat = defaultdict(list)
        for node in tree.xpath('//field[@name="vat_label"]'):
            try:
                label = node.text or literal_eval(node.get('eval'))
            except ValueError:
                continue    # next one!

            vat[label].append(node.getparent().get('id'))

        value_for['vat_label'] = list(vat.items())

        names = defaultdict(list)

        name_update = 'ad af ba cd ci gf gp gu hm kg kh kn md mq nc pf pn ps re sh st vc wf'
        matches = ' or '.join('@id="{}"'.format(n) for n in name_update.split())
        for node in tree.xpath('//record[{}]/field[@name="name"]'.format(matches)):
            names[node.text] = [node.getparent().get('id')]

        value_for['name'] = list(names.items())

        india = tree.find('//record[@id="in"]/field[@name="address_format"]')
        value_for['address_format'] = [(literal_eval(india.get('eval')), ['in'])]

    for f in value_for:
        cr.executemany("""
            UPDATE res_country
               SET {}=%s
             WHERE id IN (SELECT res_id
                            FROM ir_model_data
                           WHERE model='res.country'
                             AND module='base'
                             AND name=ANY(%s))
        """.format(f), value_for[f])
