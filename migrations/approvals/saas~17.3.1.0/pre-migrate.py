from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "approvals.approval_request_request_owner_rule")
    util.remove_record(cr, "approvals.approval_request_write_request_owner_rule")
    util.remove_record(cr, "approvals.approval_request_approvers_rule")
