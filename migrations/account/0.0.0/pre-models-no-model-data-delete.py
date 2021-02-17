# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.ENVIRON["no_model_data_delete"].update(
        {
            "account.tax.group": "unused",
            "account.payment.term": "unused",
        }
    )
