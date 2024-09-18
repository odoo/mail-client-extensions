from odoo.upgrade import util


def migrate(cr, version):
    cr.execute("ALTER TABLE res_users_studio_approval_rule_rel RENAME TO approval_rule_users_to_notify_rel")
    util.rename_field(cr, "studio.approval.rule", "group_id", "approval_group_id")
    util.remove_field(cr, "studio.approval.entry", "group_id")
