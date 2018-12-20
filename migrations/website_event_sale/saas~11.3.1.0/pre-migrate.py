# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.rename_xmlid(cr, 'website_event_sale.cart','website_event_sale.cart_lines_inherit_website_event_sale')

