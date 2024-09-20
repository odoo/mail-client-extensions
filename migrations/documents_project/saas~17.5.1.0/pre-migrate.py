from odoo.upgrade import util


def migrate(cr, version):
    # TODO: fill documents redirect, move folder id field, folder structure, etc
    util.remove_view(cr, "documents_project.tag_view_form_inherit")

    util.remove_field(cr, "project.task", "shared_document_count")
    util.remove_field(cr, "project.task", "shared_document_ids")

    util.remove_field(cr, "project.project", "shared_document_count")
    util.remove_field(cr, "project.project", "shared_document_ids")
    util.remove_field(cr, "project.project", "is_shared")
