from odoo.upgrade import util


def migrate(cr, version):
    """
    Here we try to match changes from this module xml data.

    Here's this module `multi` server actions, along with their children and a [TAG] if changed:
    - `documents_project.ir_actions_server_mark_as_draft`
        - `documents_project.ir_actions_server_mark_as_draft_code`
        - [NEW] `documents_project.ir_actions_server_mark_as_draft_tag_remove_to_validate`
        - [NEW] `documents_project.ir_actions_server_mark_as_draft_tag_add_draft`
        - [NEW] `documents_project.ir_actions_server_mark_as_draft_remove_activities`

    - `documents_project.ir_actions_server_ask_for_validation`
        - `documents_project.ir_actions_server_ask_for_validation_code`
        - [NEW] `documents_project.ir_actions_server_ask_for_validation_tag_remove_validated`
        - [NEW] `documents_project.ir_actions_server_ask_for_validation_tag_remove_draft`
        - [NEW] `documents_project.ir_actions_server_ask_for_validation_tag_add_to_validate`
        - [NEW] `documents_project.ir_actions_server_ask_for_validation_create_activity`

    - [RENAMED] `documents_project.ir_actions_server_validate`
        - `documents_project.ir_actions_server_validate_code`
        - [NEW] `documents_project.ir_actions_server_validate_tag_remove_draft`
        - [NEW] `documents_project.ir_actions_server_validate_tag_remove_to_validate`
        - [NEW] `documents_project.ir_actions_server_validate_tag_add_validated`
        - [NEW] `documents_project.ir_actions_server_validate_remove_activities`

    - `documents_project.ir_actions_server_create_project_deprecate`
        - [NEW] `documents_project.ir_actions_server_create_project_deprecate_tag_remove_to_validate`
        - [NEW] `documents_project.ir_actions_server_create_project_deprecate_tag_remove_validated`
        - [NEW] `documents_project.ir_actions_server_create_project_deprecate_tag_remove_draft`
        - [NEW] `documents_project.ir_actions_server_create_project_deprecate_tag_add_deprecated`
        - [NEW] `documents_project.ir_actions_server_create_project_deprecate_remove_activities`

    Also these actions have been removed:
    - `documents_project.ir_actions_server_tag_remove_draft`
    - `documents_project.ir_actions_server_tag_remove_to_validate`
    - `documents_project.ir_actions_server_tag_remove_validated`
    - `documents_project.ir_actions_server_tag_remove_deprecated`
    - `documents_project.ir_actions_server_tag_add_draft`
    - `documents_project.ir_actions_server_tag_add_to_validate`
    - `documents_project.ir_actions_server_tag_add_validated`
    - `documents_project.ir_actions_server_tag_add_deprecated`
    """

    util.rename_xmlid(
        cr,
        old="documents_project.ir_actions_server_ask_validate",
        new="documents_project.ir_actions_server_validate",
    )

    # dict shape: { parent: { new: origin }}
    child_xmlids_changes_by_parent = {
        "documents_project.ir_actions_server_mark_as_draft": {
            "documents_project.ir_actions_server_mark_as_draft_tag_remove_to_validate": "documents_project.ir_actions_server_tag_remove_to_validate",
            "documents_project.ir_actions_server_mark_as_draft_tag_add_draft": "documents_project.ir_actions_server_tag_add_draft",
            "documents_project.ir_actions_server_mark_as_draft_remove_activities": "documents.ir_actions_server_remove_activities",
        },
        "documents_project.ir_actions_server_ask_for_validation": {
            "documents_project.ir_actions_server_ask_for_validation_tag_remove_validated": "documents_project.ir_actions_server_tag_remove_validated",
            "documents_project.ir_actions_server_ask_for_validation_tag_remove_draft": "documents_project.ir_actions_server_tag_remove_draft",
            "documents_project.ir_actions_server_ask_for_validation_tag_add_to_validate": "documents_project.ir_actions_server_tag_add_to_validate",
            "documents_project.ir_actions_server_ask_for_validation_create_activity": "documents.ir_actions_server_create_activity",
        },
        "documents_project.ir_actions_server_validate": {
            "documents_project.ir_actions_server_validate_tag_remove_draft": "documents_project.ir_actions_server_tag_remove_draft",
            "documents_project.ir_actions_server_validate_tag_remove_to_validate": "documents_project.ir_actions_server_tag_remove_to_validate",
            "documents_project.ir_actions_server_validate_tag_add_validated": "documents_project.ir_actions_server_tag_add_validated",
            "documents_project.ir_actions_server_validate_remove_activities": "documents.ir_actions_server_remove_activities",
        },
        "documents_project.ir_actions_server_create_project_deprecate": {
            "documents_project.ir_actions_server_create_project_deprecate_tag_remove_to_validate": "documents_project.ir_actions_server_tag_remove_to_validate",
            "documents_project.ir_actions_server_create_project_deprecate_tag_remove_validated": "documents_project.ir_actions_server_tag_remove_validated",
            "documents_project.ir_actions_server_create_project_deprecate_tag_remove_draft": "documents_project.ir_actions_server_tag_remove_draft",
            "documents_project.ir_actions_server_create_project_deprecate_tag_add_deprecated": "documents_project.ir_actions_server_tag_add_deprecated",
            "documents_project.ir_actions_server_create_project_deprecate_remove_activities": "documents.ir_actions_server_remove_activities",
        },
    }
    util.import_script("base/saas~18.2.1.3/pre-ir_act_server.py").rematch_xmlids(
        cr, child_xmlids_changes_by_parent, mute_missing_child=True
    )

    # Those xmlids no longer exist,
    # they should have been renamed above unless they are unused.
    # So we delete them just to make sure.
    util.delete_unused(
        cr,
        "documents_project.ir_actions_server_tag_remove_draft",
        "documents_project.ir_actions_server_tag_remove_to_validate",
        "documents_project.ir_actions_server_tag_remove_validated",
        "documents_project.ir_actions_server_tag_remove_deprecated",
        "documents_project.ir_actions_server_tag_add_draft",
        "documents_project.ir_actions_server_tag_add_to_validate",
        "documents_project.ir_actions_server_tag_add_validated",
        "documents_project.ir_actions_server_tag_add_deprecated",
    )
