# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.replace_record_references_batch(
        cr,
        {
            util.ref(cr, "l10n_be.tax_group_tva_0_eu"): util.ref(cr, "l10n_be.tax_group_tva_0"),
            util.ref(cr, "l10n_be.tax_group_tva_6_eu"): util.ref(cr, "l10n_be.tax_group_tva_6"),
            util.ref(cr, "l10n_be.tax_group_tva_12_eu"): util.ref(cr, "l10n_be.tax_group_tva_12"),
            util.ref(cr, "l10n_be.tax_group_tva_21_eu"): util.ref(cr, "l10n_be.tax_group_tva_21"),
            util.ref(cr, "l10n_be.tax_group_tva_6_non_eu"): util.ref(cr, "l10n_be.tax_group_tva_6"),
            util.ref(cr, "l10n_be.tax_group_tva_12_non_eu"): util.ref(cr, "l10n_be.tax_group_tva_12"),
            util.ref(cr, "l10n_be.tax_group_tva_21_non_eu"): util.ref(cr, "l10n_be.tax_group_tva_21"),
            util.ref(cr, "l10n_be.tax_group_tva_6_cocont"): util.ref(cr, "l10n_be.tax_group_tva_6"),
            util.ref(cr, "l10n_be.tax_group_tva_12_cocont"): util.ref(cr, "l10n_be.tax_group_tva_12"),
            util.ref(cr, "l10n_be.tax_group_tva_21_cocont"): util.ref(cr, "l10n_be.tax_group_tva_21"),
            util.ref(cr, "l10n_be.tax_group_tva_21_50_deductible"): util.ref(cr, "l10n_be.tax_group_tva_21"),
        },
        "account.tax.group",
        replace_xmlid=False,
    )

    util.remove_record(cr, "l10n_be.tax_group_tva_0_eu")
    util.remove_record(cr, "l10n_be.tax_group_tva_6_eu")
    util.remove_record(cr, "l10n_be.tax_group_tva_12_eu")
    util.remove_record(cr, "l10n_be.tax_group_tva_21_eu")
    util.remove_record(cr, "l10n_be.tax_group_tva_6_non_eu")
    util.remove_record(cr, "l10n_be.tax_group_tva_12_non_eu")
    util.remove_record(cr, "l10n_be.tax_group_tva_21_non_eu")
    util.remove_record(cr, "l10n_be.tax_group_tva_6_cocont")
    util.remove_record(cr, "l10n_be.tax_group_tva_12_cocont")
    util.remove_record(cr, "l10n_be.tax_group_tva_21_cocont")
    util.remove_record(cr, "l10n_be.tax_group_tva_21_50_deductible")
