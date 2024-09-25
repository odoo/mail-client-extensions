from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "documents_project.documents_project_status_draft")
    util.remove_record(cr, "documents_project.documents_project_status_to_validate")
    util.remove_record(cr, "documents_project.documents_project_status_validated")
    util.remove_record(cr, "documents_project.documents_project_status_deprecated")
