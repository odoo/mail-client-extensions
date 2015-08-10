# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util
from lxml import etree


def migrate(cr, version):
    with util.skippable_cm(), util.edit_view(cr, 'sale.report_saleorder_document') as arch:
        node = etree.fromstring('<t t-set="o" t-value="doc"/>')
        arch[0].insert(0, node)
        node = arch.find('.//div[@t-if="o.payment_term"]')
        if node:
            node.set('name', 'payment_term')
