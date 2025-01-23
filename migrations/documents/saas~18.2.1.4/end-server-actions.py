from odoo.upgrade import util


def migrate(cr, version):
    util.delete_unused(
        cr,
        "documents.ir_actions_server_remove_tags",
        "documents.ir_actions_server_create_activity",
        "documents.ir_actions_server_remove_activities",
        "documents.ir_actions_server_tag_remove_inbox",
        "documents.ir_actions_server_tag_remove_to_validate",
        "documents.ir_actions_server_tag_add_bill",
    )
