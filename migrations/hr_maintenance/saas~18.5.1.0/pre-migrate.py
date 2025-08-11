from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "res.users", "equipment_ids")
    util.remove_field(cr, "res.users", "equipment_count")

    util.remove_view(cr, "hr_maintenance.res_users_view_form_preference")
