from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_view(cr, "snailmail_account_followup.followup_send_wizard_form")
    util.remove_record(cr, "snailmail_account_followup.followup_send")

    util.remove_model(cr, "followup.send")
    util.remove_model(cr, "snailmail.confirm.followup")
