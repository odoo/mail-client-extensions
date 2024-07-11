from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "mrp.production", "confirm_cancel")
    if util.module_installed(cr, "mrp_workorder"):
        eb = util.expand_braces
        util.rename_xmlid(cr, *eb("mrp{,_workorder}.workcenter_line_gantt_production"))
        util.rename_xmlid(cr, *eb("mrp{,_workorder}.mrp_workorder_view_gantt"))
    else:
        util.remove_view(cr, "mrp.workcenter_line_gantt_production")
        util.remove_view(cr, "mrp.mrp_workorder_view_gantt")
        util.remove_act_window_view_mode(cr, "mrp.workorder", "gantt")
