from odoo.upgrade import util


def migrate(cr, version):
    ir_action_id = util.ref(cr, "documents_sign.ir_actions_server_create_sign_template_direct")
    if ir_action_id:
        cr.execute(
            """
            UPDATE ir_actions
               SET binding_model_id = NULL,
                   binding_view_types = NULL
             WHERE id = %s
        """,
            (ir_action_id,),
        )
