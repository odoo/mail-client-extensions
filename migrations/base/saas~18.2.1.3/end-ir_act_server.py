from odoo.upgrade import util


def migrate(cr, version):
    util.remove_column(cr, "ir_act_server", "_upg_orig_id")
    util.remove_column(cr, "ir_act_server", "_upg_matched")
