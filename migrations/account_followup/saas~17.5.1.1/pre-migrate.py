from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_field(cr, "account.move.line", "last_followup_date")
    util.remove_field(cr, "account.move.line", "next_action_date")
