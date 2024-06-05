from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "saas_trial.ir_cron_view_hide_doall")
