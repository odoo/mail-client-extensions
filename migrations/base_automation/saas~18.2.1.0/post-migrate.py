from odoo.upgrade import util


def migrate(cr, version):
    cron = util.ref(cr, "base_automation.ir_cron_data_base_automation_check")
    if cron:
        util.env(cr)["ir.cron"].browse([cron]).ir_actions_server_id.code = "model._cron_process_time_based_actions()"
