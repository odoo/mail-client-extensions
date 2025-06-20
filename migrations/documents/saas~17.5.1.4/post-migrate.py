from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(cr, "documents.mail_template_document_request", util.update_record_from_xml)
    util.if_unchanged(cr, "documents.mail_template_document_request_reminder", util.update_record_from_xml)
    util.if_unchanged(cr, "documents.public_page_layout", util.update_record_from_xml)

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

    for folder in ["internal", "finance"]:
        if not util.ref(cr, f"documents.document_{folder}_folder"):
            util.update_record_from_xml(cr, f"documents.document_{folder}_folder")
            util.force_noupdate(cr, f"documents.document_{folder}_folder")
            util.force_noupdate(cr, f"documents.document_{folder}_folder_mail_alias")

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
