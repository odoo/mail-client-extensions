from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "documents_project.action_view_documents_project_task")
    util.remove_record(cr, "documents_project.action_view_documents_project_project")
    util.remove_record(cr, "documents_project.ir_actions_server_create_project_task")
    util.remove_record(cr, "documents_project.ir_actions_server_create_a_task_code")

    util.remove_record(cr, "documents_project.public_page_layout")
    util.remove_record(cr, "documents_project.public_project_page")
    util.remove_record(cr, "documents_project.public_task_page")
    util.remove_record(cr, "documents_project.portal_my_task")
    util.remove_record(cr, "documents_project.portal_tasks_list")

    util.remove_view(cr, "documents_project.document_view_search_inherit")
    util.remove_view(cr, "documents_project.view_task_form2_document_inherit")
    util.remove_view(cr, "documents_project.project_sharing_project_task_view_form_inherit")

    util.remove_field(cr, "documents.document", "project_id")
    util.remove_field(cr, "documents.document", "task_id")
    util.remove_field(cr, "project.task", "document_ids")
    util.remove_field(cr, "project.task", "document_count")
    util.remove_field(cr, "project.task", "documents_folder_id")
    util.remove_field(cr, "project.task", "folder_user_permission")
    util.remove_field(cr, "project.task", "project_use_documents")
