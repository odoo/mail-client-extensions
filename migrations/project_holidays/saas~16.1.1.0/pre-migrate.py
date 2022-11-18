from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "project_holidays.view_task_search_form_inherit_holidays")
