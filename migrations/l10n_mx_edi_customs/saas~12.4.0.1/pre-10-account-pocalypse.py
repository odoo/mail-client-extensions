# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    pv = util.parse_version
    if pv(version) >= pv("saas~12.4"):
        # This script is also linked from `l10n_mx_edi@saas~12.5` (modules merged)
        # But should only be called for databases older than saas~12.4
        return

    util.create_column(cr, "account_move_line", "l10n_mx_edi_customs_number", "varchar")

    if util.column_exists(cr, "account_invoice_line", "l10n_mx_edi_customs_number"):
        # if run from `l10n_mx_edi@saas~12.5`, column may not exists if the module was not installed
        cr.execute(
            """
            UPDATE account_move_line aml
               SET l10n_mx_edi_customs_number = invl.l10n_mx_edi_customs_number
              FROM invl_aml_mapping m
              JOIN account_invoice_line invl ON invl.id = m.invl_id
             WHERE m.aml_id = aml.id
            """
        )
