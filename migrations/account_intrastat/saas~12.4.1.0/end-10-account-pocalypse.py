# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    cr.execute(
        """
        UPDATE account_move am
           SET intrastat_transport_mode_id = inv.intrastat_transport_mode_id,
               intrastat_country_id = inv.intrastat_country_id
          FROM account_invoice inv
         WHERE am.id = inv.move_id
    """
    )

    cr.execute(
        """
        UPDATE account_move_line aml
           SET intrastat_transaction_id = invl.intrastat_transaction_id
          FROM invl_aml_mapping m
          JOIN account_invoice_line invl ON invl.id = m.invl_id
         WHERE m.aml_id = aml.id
        """
    )
