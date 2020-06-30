# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "website_page", "header_visible", "boolean", default=True)
    util.create_column(cr, "website_page", "footer_visible", "boolean", default=True)
