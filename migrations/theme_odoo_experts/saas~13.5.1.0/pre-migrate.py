# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "theme_odoo_experts.assets_frontend")
    util.remove_record(cr, "theme_odoo_experts._assets_frontend_helpers")
    util.remove_record(cr, "theme_odoo_experts.odoo_experts_snippet_options")
