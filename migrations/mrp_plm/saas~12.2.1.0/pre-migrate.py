# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "mrp_eco_approval", "approval_date", 'timestamp without time zone')
    util.create_column(cr, "mrp_eco_approval", "is_closed", 'boolean')
