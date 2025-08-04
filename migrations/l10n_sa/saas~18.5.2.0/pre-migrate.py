from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "l10n_sa.arabic_english_invoice")
    util.if_unchanged(
        cr, "l10n_sa.paperformat_l10n_sa_a4", util.update_record_from_xml, fields=["header_spacing", "margin_top"]
    )
