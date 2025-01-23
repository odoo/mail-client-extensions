from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "base_automation.ir_actions_server_view_form_automation")
