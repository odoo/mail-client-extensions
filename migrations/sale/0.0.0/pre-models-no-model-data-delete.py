# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.ENVIRON["no_model_data_delete"].update(
        {
            "sale.order": "always",
            "sale.order.line": "always",
        }
    )
