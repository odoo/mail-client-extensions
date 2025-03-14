from odoo.upgrade import util


def migrate(cr, version):
    util.update_record_from_xml(cr, "l10n_pl.account_tax_report_line_podatek_uslug_pozostalych")
