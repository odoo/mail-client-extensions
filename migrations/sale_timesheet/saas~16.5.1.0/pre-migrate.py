from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "sale_timesheet.project_project_view_form_simplified_inherit")
    util.remove_field(cr, "project.project", "display_create_order")
    util.create_column(cr, "project_project", "billing_type", "character varying", default="not_billable")
