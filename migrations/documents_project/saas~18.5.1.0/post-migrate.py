from odoo.upgrade import util


def migrate(cr, version):
    # remove demo data
    util.delete_unused(
        cr,
        "documents_project.ir_actions_server_mark_as_draft",
        "documents_project.ir_actions_server_mark_as_draft_code",
        "documents_project.ir_actions_server_mark_as_draft_tag_remove_to_validate",
        "documents_project.ir_actions_server_mark_as_draft_tag_add_draft",
        "documents_project.ir_actions_server_mark_as_draft_remove_activities",
        "documents_project.ir_actions_server_ask_for_validation",
        "documents_project.ir_actions_server_ask_for_validation_code",
        "documents_project.ir_actions_server_ask_for_validation_tag_remove_validated",
        "documents_project.ir_actions_server_ask_for_validation_tag_remove_draft",
        "documents_project.ir_actions_server_ask_for_validation_tag_add_to_validate",
        "documents_project.ir_actions_server_ask_for_validation_create_activity",
        "documents_project.ir_actions_server_validate",
        "documents_project.ir_actions_server_validate_code",
        "documents_project.ir_actions_server_validate_tag_remove_draft",
        "documents_project.ir_actions_server_validate_tag_remove_to_validate",
        "documents_project.ir_actions_server_validate_tag_add_validated",
        "documents_project.ir_actions_server_validate_remove_activities",
        "documents_project.ir_actions_server_create_project_deprecate",
        "documents_project.ir_actions_server_create_project_deprecate_tag_remove_to_validate",
        "documents_project.ir_actions_server_create_project_deprecate_tag_remove_validated",
        "documents_project.ir_actions_server_create_project_deprecate_tag_remove_draft",
        "documents_project.ir_actions_server_create_project_deprecate_tag_add_deprecated",
        "documents_project.ir_actions_server_create_project_deprecate_remove_activities",
    )
