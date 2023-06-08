# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "mrp_account_enterprise.mrp_production_form_inherit_view6")
