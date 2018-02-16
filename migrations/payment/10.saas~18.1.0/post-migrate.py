# -*- coding: utf-8 -*-
from contextlib import closing
from lxml import etree

from odoo.addons.base.maintenance.migrations import util
from odoo.tools import file_open
from odoo.tools.safe_eval import safe_eval

def migrate(cr, version):
    ref = lambda x: util.ref(cr, x)     # noqa
    Acquirers = util.env(cr)['payment.acquirer']

    with closing(file_open('addons/payment/data/payment_acquirer_data.xml')) as fp:
        tree = etree.parse(fp)
        for node in tree.xpath('//record[@model="payment.acquirer"]/field[@name="payment_icon_ids"]'):
            icons = safe_eval(node.get('eval'), {'ref': ref})
            aid = ref('payment.' + node.getparent().get('id'))
            Acquirers.browse(aid).write({'payment_icon_ids': icons})
