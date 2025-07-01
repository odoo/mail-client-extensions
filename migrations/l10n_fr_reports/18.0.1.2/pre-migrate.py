from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "account.report.async.export", "company_id")
