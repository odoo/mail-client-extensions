from odoo.upgrade import util


def migrate(cr, version):
    # The server actions need to be created but they are not loaded during the load of the module
    # So they are created manually together with the referenced tags and folder.
    if not util.ref(cr, "documents.documents_tag_deprecated"):
        util.update_record_from_xml(cr, "documents.documents_tag_deprecated")

    server_actions = [
        "tag_remove_draft",
        "tag_remove_to_validate",
        "tag_remove_validated",
        "tag_remove_deprecated",
        "tag_add_draft",
        "tag_add_to_validate",
        "tag_add_validated",
        "tag_add_deprecated",
        "create_a_task_code",
        "create_project_task",
        "deprecate_code",
        "create_project_deprecate",
        "mark_as_draft_code",
        "mark_as_draft",
        "ask_for_validation_code",
        "ask_for_validation",
        "validate_code",
        "ask_validate",
    ]
    for server_action in server_actions:
        util.update_record_from_xml(cr, f"documents_project.ir_actions_server_{server_action}")
