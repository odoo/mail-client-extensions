# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    gone = """
        # account.fiscal.position.tax.template
        fp_tax_template_impexp_ha_encaissement
        fp_tax_template_impexp_ha_intermediaire
        fp_tax_template_impexp_ha_encaissement_super_reduite
        fp_tax_template_impexp_ha_encaissement_reduite

        # account.tax.template
        tva_import_0

        # account.tax.report.line
        # Other computed dynamically, see bellow
        tax_report_non_imp_hors_ue
        tax_report_non_imp_livraisons_intra
        tax_report_non_imp_non_imposables
        tax_report_non_imp_achats_import
        tax_report_non_imp_non_ca3
        tax_report_non_imp
    """
    for name in util.splitlines(gone):
        util.remove_record(cr, f"l10n_fr.{name}")

    for infix1 in {"base", "vat"}:
        for infix2 in {"coll", "acq", "acq_immo", "due_intra", "ded_intra"}:
            for pc in {"20", "19_6", "8_5", "10", "7", "5", "5_5", "2_1"}:
                util.remove_record(cr, f"l10n_fr.tax_report_{infix1}_{infix2}_{pc}")
            util.remove_record(cr, f"l10n_fr.tax_report_{infix1}_{infix2}")
