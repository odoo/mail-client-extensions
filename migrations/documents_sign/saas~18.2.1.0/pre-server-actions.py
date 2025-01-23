from odoo.upgrade import util


def migrate(cr, version):
    """
    Here we try to match changes from this module xml data.

    Before:
        The `documents_sign.ir_actions_server_create_sign_template_direct` parent server action
        was using `documents.ir_actions_server_create_activity` action as a child.

    After:
        The child action was duplicated in the xml data and named
        `documents_sign.ir_actions_server_create_sign_template_direct_create_activity`
    """
    util.import_script("base/saas~18.2.1.3/pre-ir_act_server.py").rematch_xmlids(
        cr,
        {
            "documents_sign.ir_actions_server_create_sign_template_direct": {
                "documents_sign.ir_actions_server_create_sign_template_direct_create_activity": "documents.ir_actions_server_create_activity"
            }
        },
    )
