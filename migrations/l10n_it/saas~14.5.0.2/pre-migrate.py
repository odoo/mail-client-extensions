# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    """
    Creates a group per tax rate, remove the old deductible ones.
    Makes 20% and 21% rates obsolete, as current rate is 22%.
    """

    refs = [
        ("l10n_it.tax_group_iva_4_de_50", "l10n_it.tax_group_iva_4"),
        ("l10n_it.tax_group_iva_10_de_50", "l10n_it.tax_group_iva_10"),
        ("l10n_it.tax_group_iva_20_de_10", "l10n_it.tax_group_iva_20"),
        ("l10n_it.tax_group_iva_20_de_15", "l10n_it.tax_group_iva_20"),
        ("l10n_it.tax_group_iva_20_de_40", "l10n_it.tax_group_iva_20"),
        ("l10n_it.tax_group_iva_20_de_50", "l10n_it.tax_group_iva_20"),
        ("l10n_it.tax_group_iva_21_inde", "l10n_it.tax_group_iva_21"),
        ("l10n_it.tax_group_iva_21_de_10", "l10n_it.tax_group_iva_21"),
        ("l10n_it.tax_group_iva_21_de_15", "l10n_it.tax_group_iva_21"),
        ("l10n_it.tax_group_iva_21_de_40", "l10n_it.tax_group_iva_21"),
        ("l10n_it.tax_group_iva_21_de_50", "l10n_it.tax_group_iva_21"),
        ("l10n_it.tax_group_iva_22_inde", "l10n_it.tax_group_iva_22"),
        ("l10n_it.tax_group_iva_22_de_10", "l10n_it.tax_group_iva_22"),
        ("l10n_it.tax_group_iva_22_de_15", "l10n_it.tax_group_iva_22"),
        ("l10n_it.tax_group_iva_22_de_40", "l10n_it.tax_group_iva_22"),
        ("l10n_it.tax_group_iva_22_de_50", "l10n_it.tax_group_iva_22"),
    ]
    idmap = {util.ref(cr, old): util.ref(cr, new) for old, new in refs}
    util.replace_record_references_batch(cr, idmap, "account.tax.group", replace_xmlid=False)
    util.delete_unused(cr, *(old for old, _new in refs))
