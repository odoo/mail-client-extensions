from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "project.personal_task_type_edit")
    util.update_field_usage(cr, "project.project", "allow_rating", "rating_active")
    util.remove_field(cr, "project.project", "allow_rating")
    util.remove_field(cr, "project.project", "doc_count")
    util.remove_field(cr, "project.task.type", "description")
    util.update_record_from_xml(cr, "base.module_category_services_project", from_module="project")
