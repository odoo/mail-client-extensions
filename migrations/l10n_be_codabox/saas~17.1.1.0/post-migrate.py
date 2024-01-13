# -*- coding: utf-8 -*-


def migrate(cr, version):
    cr.execute(
        """
        UPDATE res_company
           SET l10n_be_codabox_show_iap_token = TRUE
         WHERE l10n_be_codabox_iap_token IS NOT NULL
    """
    )
