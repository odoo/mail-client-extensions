# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "stock_picking", "website_id", "int4")
    # website_id on res_partner is a new field in saas-11.5, no need to recompute the stored related, it's always NULL.
