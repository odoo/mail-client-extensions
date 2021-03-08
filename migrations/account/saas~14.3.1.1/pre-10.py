# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # ===============================================================
    # Allow tax to not be affected by a previous one (PR:66134)
    # ===============================================================

    util.create_column(cr, 'account_tax', 'is_base_affected', 'boolean', default=True)
    util.create_column(cr, 'account_tax_template', 'is_base_affected', 'boolean', default=True)
