# -*- coding: utf-8 -*-
from contextlib import closing

from lxml import etree

from openerp.addons.base.maintenance.migrations import util
from openerp.tools import file_open

def migrate(cr, version):
    codes = []
    with closing(file_open('addons/base/res/res_country_data.xml')) as fp:
        tree = etree.parse(fp)
        for node in tree.xpath('//field[@name="phone_code"]'):
            xid = node.getparent().get('id')
            if not xid:
                continue
            try:
                phone_code = int(node.get('eval') or node.text)
            except ValueError:
                continue    # next one!

            if phone_code:
                codes.append([phone_code, xid])

    cr.executemany("""
        UPDATE res_country
           SET phone_code=%s
         WHERE id=(SELECT res_id
                     FROM ir_model_data
                    WHERE model='res.country'
                      AND module='base'
                      AND name=%s)
           AND coalesce(phone_code, 0) = 0
    """, codes)

if __name__ == '__main__':
    util.main(migrate)
