# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "account_move_line", "l10n_mx_edi_customs_number", "varchar")

    cr.execute(
        """
        UPDATE account_move_line aml
           SET l10n_mx_edi_customs_number = invl.l10n_mx_edi_customs_number
          FROM invl_aml_mapping m
          JOIN account_invoice_line invl ON invl.id = m.invl_id
         WHERE m.aml_id = aml.id
        """
    )
