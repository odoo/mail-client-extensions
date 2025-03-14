from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "hr.employee.base", "flexible_hours")
    util.remove_field(cr, "resource.resource", "flexible_hours")

    util.remove_view(cr, "planning.view_resource_resource_search_inherit")
    util.remove_view(cr, "planning.resource_resource_form_inherit_resource")
