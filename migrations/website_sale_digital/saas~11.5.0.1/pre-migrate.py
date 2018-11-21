# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    eb = util.expand_braces
    util.rename_xmlid(
        cr,
        *eb("website_sale_digital.{portal_order_page_downloads,sale_order_portal_content_inherit_website_sale_digital}")
    )
