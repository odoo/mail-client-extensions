# -*- coding: utf-8 -*-
from odoo.upgrade import util
from odoo.upgrade.util import accounting


def migrate(cr, version):
    # All taxes xmlid in the upgraded tax.template
    upgraded_tax_xmlid = [
        "tva_normale",
        "tva_intermediaire_encaissement",
        "tva_normale_encaissement",
        "tva_specifique",
        "tva_intermediaire",
        "tva_reduite",
        "tva_reduite_encaissement",
        "tva_super_reduite",
        "tva_super_reduite_encaissement",
        "tva_normale_ttc",
        "tva_intermediaire_encaissement_ttc",
        "tva_normale_encaissement_ttc",
        "tva_specifique_ttc",
        "tva_intermediaire_ttc",
        "tva_reduite_ttc",
        "tva_reduite_encaissement_ttc",
        "tva_super_reduite_ttc",
        "tva_super_reduite_encaissement_ttc",
        "tva_acq_normale",
        "tva_acq_encaissement",
        "tva_acq_intermediaire_encaissement",
        "tva_acq_specifique",
        "tva_acq_intermediaire",
        "tva_acq_reduite",
        "tva_acq_encaissement_reduite",
        "tva_acq_super_reduite",
        "tva_acq_encaissement_super_reduite",
        "tva_acq_normale_TTC",
        "tva_acq_encaissement_TTC",
        "tva_acq_specifique_TTC",
        "tva_acq_intermediaire_encaissement_TTC",
        "tva_acq_intermediaire_TTC",
        "tva_acq_reduite_TTC",
        "tva_acq_encaissement_reduite_TTC",
        "tva_acq_super_reduite_TTC",
        "tva_acq_encaissement_super_reduite_TTC",
        "tva_imm_normale",
        "tva_imm_specifique",
        "tva_imm_intermediaire",
        "tva_imm_reduite",
        "tva_imm_super_reduite",
        "tva_intra_normale",
        "tva_intra_specifique",
        "tva_intra_intermediaire",
        "tva_intra_reduite",
        "tva_intra_super_reduite",
        "tva_0",
        "tva_export_0",
        "tva_intra_0",
        "tva_import_0",
        "tva_import_outside_eu_20",
        "tva_import_outside_eu_10",
        "tva_import_outside_eu_8_5",
        "tva_import_outside_eu_5_5",
        "tva_import_outside_eu_2_1",
    ]
    env = util.env(cr)
    l10n_fr_chart_template_id = env["ir.model.data"].xmlid_to_res_id("l10n_fr.l10n_fr_pcg_chart_template")
    companies = env["res.company"].search([("chart_template_id", "=", l10n_fr_chart_template_id)])
    for company in companies:
        accounting.upgrade_tax_tags(
            cr, env, company, chart_template_id=l10n_fr_chart_template_id, upgraded_tax_xmlid=upgraded_tax_xmlid
        )
