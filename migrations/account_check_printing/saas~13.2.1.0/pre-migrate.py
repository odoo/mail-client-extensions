# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "account_payment", "check_number_int", "integer")
    cr.execute(
        r"""
        UPDATE account_payment
           SET check_number_int = CASE WHEN check_number ~ '^\s*\d+\s*$' AND check_number::numeric <= 2147483647
                                       THEN check_number::integer
                                       ELSE 0
                                   END
    """
    )

    countries = [cc for cc in ["us", "ca"] if util.module_installed(cr, f"l10n_{cc}")]

    if countries:
        cr.execute(
            """
            UPDATE res_company c
               SET account_check_printing_layout = CONCAT('l10n_',
                                                          lower(t.code),
                                                          '_check_printing.',
                                                          c.account_check_printing_layout)
              FROM res_partner p
              JOIN res_country t ON t.id = p.country_id
             WHERE p.id = c.partner_id
               AND c.account_check_printing_layout IS NOT NULL
               AND c.account_check_printing_layout != 'disabled'
               AND lower(t.code) = ANY(%s)
        """,
            [countries],
        )

        for cc in countries:
            util.force_install_module(cr, f"l10n_{cc}_check_printing")

    # the value `action_print_check_top` was the default value, but make no sense for
    # non-us/non-ca companies
    cr.execute(
        r"""
            UPDATE res_company
               SET account_check_printing_layout = 'disabled'
             WHERE account_check_printing_layout NOT LIKE 'l10n\_%'
        """
    )
