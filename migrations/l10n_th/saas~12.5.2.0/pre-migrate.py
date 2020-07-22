# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    cr.execute(
        """
        SELECT name
          FROM ir_model_data
         WHERE module = 'l10n_th'
           AND model = 'account.tax.report.line'
    """
    )
    for name in cr.fetchall():
        util.remove_record(cr, "l10n_th." + name[0])

    util.remove_record(cr, "l10n_th.tax_group_7")
    util.delete_unused(cr, "l10n_th.acc_type_other")
