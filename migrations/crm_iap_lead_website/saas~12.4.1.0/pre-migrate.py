# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "crm_reveal_rule", "website_id", "int4")
