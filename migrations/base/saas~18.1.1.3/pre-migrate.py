from odoo.upgrade import util


def migrate(cr, version):
    util.change_field_selection_values(cr, "ir.actions.act_window", "target", {"inline": "current"})
    util.remove_column(cr, "ir_act_server", "model_name")

    cr.execute("DROP INDEX IF EXISTS res_device_log__composite_idx")

    util.remove_field(cr, "res.partner", "title")
    util.remove_model(cr, "res.partner.title")
