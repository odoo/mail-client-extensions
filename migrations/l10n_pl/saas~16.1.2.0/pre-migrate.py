from odoo.upgrade import util


def migrate(cr, version):
    util.update_record_from_xml(cr, "l10n_pl.account_tax_report_line_uslugi_kraj_0_tag")

    xmlids_to_remove = [
        "account_tax_report_line_towary_art_129_formula",
        "account_tax_report_line_uslug_s_trwale_formula",
        "account_tax_report_line_kasy_rejestrujace_formula",
        "account_tax_report_line_zaniechaniem_poboru_formula",
        "account_tax_report_line_podatek_art_14_5_formula",
        "account_tax_report_line_podatek_transp_termin_formula",
        "account_tax_report_line_podatek_deklaracji_formula",
        "account_tax_report_line_podatek_s_trwale_formula",
        "account_tax_report_line_podatek_s_trwalych_formula",
        "account_tax_report_line_podatek_pozostalych_nabyc_formula",
        "account_tax_report_line_podatek_okresie_formula",
    ]

    for name in xmlids_to_remove:
        util.remove_record(cr, "l10n_pl." + name)
