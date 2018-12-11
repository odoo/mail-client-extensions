# -*- coding: utf-8 -*-

from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.remove_view(cr, 'product_expiry.report_delivery_document_inherit_product_expiry')
