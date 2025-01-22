from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "report.project.task.user", "active")
    if util.module_installed(cr, "website_project"):
        util.move_field_to_module(cr, "project.task", "email_from", "website_project", "project")
