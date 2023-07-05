from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(cr, "approvals.approval_approver_user_read_own", util.update_record_from_xml)
