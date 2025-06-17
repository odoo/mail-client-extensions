from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "account_reports.action_open_view_account_return")
