from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_record(cr, "l10n_ch.l10n_ch_qr_header")
    util.remove_view(cr, "l10n_ch.qr_report_header")
    util.remove_view(cr, "l10n_ch.l10n_ch_header_template")
