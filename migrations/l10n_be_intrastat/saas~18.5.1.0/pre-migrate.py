from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "l10n_be_intrastat.vat_return_submission_wizard_form")
    util.remove_field(cr, "l10n_be_reports.vat.return.submission.wizard", "need_intrastat_goods_report")
    util.remove_view(cr, "l10n_be_intrastat.account_return_kanban_view")
