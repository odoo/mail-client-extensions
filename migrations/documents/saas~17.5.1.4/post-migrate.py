from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(cr, "documents.mail_template_document_request", util.update_record_from_xml)
    util.if_unchanged(cr, "documents.mail_template_document_request_reminder", util.update_record_from_xml)
    util.if_unchanged(cr, "documents.public_page_layout", util.update_record_from_xml)

    # The `name` of documents tags is unique in 18.0.
    # The record in documents.projects has been deleted in 18.0
    # And a new one was added in documents.
    # Since the record is `forcecreate=0`, dependant modules installed
    # during or after the upgrade will fail, so we update it and force create it.
    util.rename_xmlid(cr, "documents_project.documents_project_status_draft", "documents.documents_tag_draft")

    # The server actions need to be created but they are not loaded during the load of the module
    # So they are created manually together with the referenced tags and folder.
    tags = [
        "inbox",
        "to_validate",
        "validated",
        "bill",
        "draft",
    ]
    for tag in tags:
        if not util.ref(cr, f"documents.documents_tag_{tag}"):
            util.update_record_from_xml(cr, f"documents.documents_tag_{tag}")

    if not util.ref(cr, "documents.document_internal_folder"):
        util.update_record_from_xml(cr, "documents.document_internal_folder")

    server_actions = [
        "create_activity",
        "remove_activities",
        "remove_tags",
        "send_to_finance",
        "tag_remove_inbox",
        "tag_remove_to_validate",
        "tag_add_validated",
        "tag_add_bill",
    ]
    for action in server_actions:
        if not util.ref(cr, f"documents.ir_actions_server_{action}"):
            util.update_record_from_xml(cr, f"documents.ir_actions_server_{action}")
