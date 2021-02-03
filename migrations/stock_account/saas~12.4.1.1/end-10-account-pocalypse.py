# -*- coding: utf-8 -*-


def migrate(cr, version):
    cr.execute(
        """
        UPDATE account_move_line aml
        SET is_anglo_saxon_line = 'f'
        WHERE NOT aml.exclude_from_invoice_tab
    """
    )
