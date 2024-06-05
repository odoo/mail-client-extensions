from odoo.upgrade import util


def migrate(cr, version):
    cr.execute("""
        ALTER TABLE hr_leave_allocation
      RENAME COLUMN private_name
                 TO name
    """)
    util.update_field_usage(cr, "hr.leave.allocation", "private_name", "name")
    util.remove_field(cr, "hr.leave.allocation", "private_name")
