from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "res_company", "planning_employee_unavailabilities", "varchar", default="switch")
    cr.execute(
        """
        UPDATE res_company
           SET planning_employee_unavailabilities = 'unassign'
         WHERE planning_allow_self_unassign = true
        """
    )
    util.remove_field(cr, "res.company", "planning_allow_self_unassign")
    util.remove_field(cr, "res.config.settings", "planning_allow_self_unassign")
