# -*- coding: utf-8 -*-


def migrate(cr, version):
    cr.execute(
        """
        UPDATE account_move_line aml
           SET purchase_line_id = invl.purchase_line_id
          FROM invl_aml_mapping m
          JOIN account_invoice_line invl ON invl.id = m.invl_id
         WHERE m.aml_id = aml.id
        """
    )
