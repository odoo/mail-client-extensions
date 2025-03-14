from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_field(cr, "account.move", "l10n_ch_isr_number_spaced")
    util.remove_field(cr, "account.move", "l10n_ch_isr_optical_line")
    util.remove_field(cr, "account.move", "l10n_ch_isr_sent")
    util.remove_field(cr, "account.move", "l10n_ch_isr_valid")
    util.remove_field(cr, "account.move", "l10n_ch_isr_number")
    util.remove_field(cr, "account.move", "l10n_ch_isr_subscription_formatted")
    util.remove_field(cr, "account.move", "l10n_ch_isr_subscription")
    util.remove_field(cr, "account.move", "l10n_ch_currency_name")
    util.remove_field(cr, "account.move", "l10n_ch_isr_needs_fixing")

    util.remove_field(cr, "res.partner.bank", "l10n_ch_postal")
    util.remove_field(cr, "res.partner.bank", "l10n_ch_isr_subscription_eur")
    util.remove_field(cr, "res.partner.bank", "l10n_ch_isr_subscription_chf")
    util.rename_field(cr, "res.partner.bank", "l10n_ch_show_subscription", "l10n_ch_display_qr_bank_options")

    util.remove_field(cr, "res.config.settings", "l10n_ch_isr_scan_line_top")
    util.remove_field(cr, "res.config.settings", "l10n_ch_isr_scan_line_left")
    util.remove_field(cr, "res.config.settings", "l10n_ch_isr_print_bank_location")
    util.remove_field(cr, "res.config.settings", "l10n_ch_isr_preprinted_bank")
    util.remove_field(cr, "res.config.settings", "l10n_ch_isr_preprinted_account")

    util.remove_field(cr, "res.company", "l10n_ch_isr_print_bank_location")
    util.remove_field(cr, "res.company", "l10n_ch_isr_scan_line_top")
    util.remove_field(cr, "res.company", "l10n_ch_isr_scan_line_left")
    util.remove_field(cr, "res.company", "l10n_ch_isr_preprinted_bank")
    util.remove_field(cr, "res.company", "l10n_ch_isr_preprinted_account")

    cr.execute(
        """
          DELETE
            FROM ir_config_parameter
           WHERE key IN ('l10n_ch.isr_preprinted_account',
                         'l10n_ch.isr_preprinted_bank',
                         'l10n_ch.isr_scan_line_top',
                         'l10n_ch.isr_scan_line_left')
        """
    )

    util.remove_field(cr, "l10n_ch.qr_invoice.wizard", "isr_inv_text")
    util.remove_field(cr, "l10n_ch.qr_invoice.wizard", "nb_isr_inv")

    util.remove_view(cr, "l10n_ch.res_config_settings_view_form")
    util.remove_view(cr, "l10n_ch.isr_invoice_search_view")
    util.remove_view(cr, "l10n_ch.isr_invoice_form")
    util.remove_view(cr, "l10n_ch.isr_partner_property_bank_tree")
    util.remove_view(cr, "l10n_ch.isr_partner_bank_tree")
    util.remove_view(cr, "l10n_ch.l10n_ch_isr_report_template")
    util.remove_record(cr, "l10n_ch.l10n_ch_isr_report")
    util.remove_view(cr, "l10n_ch.isr_report_main")
    util.remove_record(cr, "l10n_ch.l10n_ch_qr_server_action")
