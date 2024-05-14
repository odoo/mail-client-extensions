from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "hr_employee", "distance_home_work", "integer")
    util.create_column(cr, "hr_employee", "distance_home_work_unit", "varchar", default="kilometers")
    cr.execute(
        """
        UPDATE hr_employee
            SET distance_home_work = km_home_work
        """
    )
