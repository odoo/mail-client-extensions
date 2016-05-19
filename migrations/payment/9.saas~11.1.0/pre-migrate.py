# -*- coding: utf-8 -*-
from lxml import etree
from openerp.addons.base.maintenance.migrations import util
from openerp.modules.module import get_module_resource

def migrate(cr, version):
    util.create_column(cr, 'payment_acquirer', 'module_id', 'int4')
    util.create_column(cr, 'payment_acquirer', 'description', 'text')

    cr.execute("UPDATE payment_acquirer SET environment='test' WHERE environment != 'prod'")

    case_query = ""
    case_params = []

    with open(get_module_resource('payment', 'data', 'payment_acquirer.xml')) as fp:
        tree = etree.parse(fp)
        for node in tree.xpath('//field[@name="description"]'):
            xid = node.getparent().get('id')
            acq = xid[len('payment_acquirer_'):]

            util.rename_xmlid(cr, '{0}.{1}'.format(acq, xid), 'payment.{0}'.format(xid))

            desc = ''.join(map(etree.tostring, node.iterchildren()))
            case_query += "WHEN provider=%s THEN %s "
            case_params.extend([acq, desc])

    cr.execute("""
        UPDATE payment_acquirer
           SET description = CASE {0} ELSE NULL END
    """.format(case_query), case_params)

    cr.execute("""
        UPDATE payment_acquirer a
           SET module_id = m.id
          FROM ir_module_module m
         WHERE m.name = 'payment_' || a.provider
    """)
