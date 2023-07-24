from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "timer_timer", "parent_res_model", "varchar")
    util.create_column(cr, "timer_timer", "parent_res_id", "int4")
    util.remove_field(cr, "timer.mixin", "display_timer_start_primary")
    util.remove_field(cr, "timer.mixin", "display_timer_stop")
    util.remove_field(cr, "timer.mixin", "display_timer_pause")
    util.remove_field(cr, "timer.mixin", "display_timer_resume")
