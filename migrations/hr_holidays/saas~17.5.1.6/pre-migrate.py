from odoo.upgrade import util


def migrate(cr, version):
    util.change_field_selection_values(cr, "hr.leave", "state", {"draft": "cancel"})

    util.alter_column_type(cr, "hr_leave", "request_hour_from", "float8", using="{}::double precision")
    util.alter_column_type(cr, "hr_leave", "request_hour_to", "float8", using="{}::double precision")
