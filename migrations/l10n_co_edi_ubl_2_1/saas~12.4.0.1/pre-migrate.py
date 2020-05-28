# -*- coding: utf-8 -*-


def migrate(cr, version):
    cr.execute(
        """
        ALTER TABLE account_invoice
        ALTER COLUMN l10n_co_edi_description_code_debit TYPE varchar
    """
    )
