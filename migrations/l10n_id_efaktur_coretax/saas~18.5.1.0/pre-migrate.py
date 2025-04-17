from odoo.upgrade import util


def migrate(cr, version):
    # Removing unused fields and views
    # account.move
    util.remove_field(cr, "account.move", "l10n_id_tax_number")
    util.remove_field(cr, "account.move", "l10n_id_replace_invoice_id")
    util.remove_field(cr, "account.move", "l10n_id_efaktur_range")
    util.remove_field(cr, "account.move", "l10n_id_need_kode_transaksi")
    util.remove_field(cr, "account.move", "l10n_id_available_range_count")
    util.remove_field(cr, "account.move", "l10n_id_show_kode_transaksi")

    util.remove_view(cr, "l10n_id_efaktur_coretax.account_move_efaktur_tree_view")

    # l10n_id_efaktur.efaktur.range
    util.remove_model(cr, "l10n_id_efaktur.efaktur.range")
    util.remove_view(cr, "l10n_id_efaktur_coretax.efaktur_tree_view")
    util.remove_record(cr, "l10n_id_efaktur_coretax.efaktur_invoice_action")

    # res.config.settings
    util.remove_view(cr, "l10n_id_efaktur_coretax.res_config_settings_view_form")
