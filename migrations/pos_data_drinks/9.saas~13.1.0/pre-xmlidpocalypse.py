# -*- coding: utf-8 -*-
from openerp.modules.module import get_module_resource
from openerp.addons.base.maintenance.migrations import util
from lxml import etree

def migrate(cr, version):
    with open(get_module_resource('pos_data_drinks', 'data', 'pos_data_drinks.xml')) as fp:
        tree = etree.parse(fp)
        xids = [n.attrib['id'] for n in tree.xpath('//record[not(contains(@id, "."))]')]

    for x in xids:
        util.rename_xmlid(cr, 'point_of_sale.' + x, 'pos_data_drinks.' + x)
