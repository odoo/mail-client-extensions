from odoo.upgrade.util import (
    column_exists,
    expand_braces,
    explode_execute,
    move_field_to_module,
    remove_field,
    rename_field,
    rename_xmlid,
)


def migrate(cr, version):
    remove_field(cr, "account.tax", "l10n_it_vat_due_date")

    remove_field(cr, "account.tax", "l10n_it_has_exoneration")
    rename_field(cr, "account.tax", "l10n_it_kind_exoneration", "l10n_it_exempt_reason")
    move_field_to_module(cr, "account.tax", "l10n_it_exempt_reason", "l10n_it_edi", "l10n_it")
    move_field_to_module(cr, "account.tax", "l10n_it_law_reference", "l10n_it_edi", "l10n_it")

    if column_exists(cr, "account_tax", "l10n_it_exempt_reason"):
        query = """
            UPDATE account_tax
               SET l10n_it_exempt_reason = NULL
             WHERE NOT (amount = 0 AND amount_type = 'percent')
               AND l10n_it_exempt_reason IS NOT NULL
        """
        explode_execute(cr, query, table="account_tax")

    rename_xmlid(cr, *expand_braces("{l10n_it_edi,l10n_it}.account_tax_form_l10n_it"))
