# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    cr.execute(
        """
        UPDATE account_move_line aml
           SET tax_line_id=r.invoice_tax_id
          FROM account_tax_repartition_line r
         WHERE r.id = aml.tax_repartition_line_id
           AND r.invoice_tax_id IS NOT NULL
    """
    )
    cr.execute(
        """
        UPDATE account_move_line aml
           SET tax_line_id=r.refund_tax_id
          FROM account_tax_repartition_line r
         WHERE r.id = aml.tax_repartition_line_id
           AND tax_line_id IS NULL
    """
    )
