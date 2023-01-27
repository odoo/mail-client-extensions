from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "hr.contract.history", "sign_request_ids")
