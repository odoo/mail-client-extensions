from odoo.upgrade import util


def migrate(cr, version):
    cr.execute("SELECT 1 FROM ir_module_module WHERE name = 'industry_fsm' AND demo")
    if cr.rowcount:
        # Those records are removed in a noupdate=1 function call
        # see odoo/enterprise@d7830587748d92c0dbc43c2365f5eaf6861ba4e4
        util.delete_unused(cr, "industry_fsm.planning_project_stage_0")
        util.delete_unused(cr, "industry_fsm.planning_project_stage_2")
        util.delete_unused(cr, "industry_fsm.planning_project_stage_3")
        util.delete_unused(cr, "industry_fsm.planning_project_stage_4")
