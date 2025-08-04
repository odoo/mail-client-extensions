from odoo.upgrade import util

ai_fields_18_pre_migrate = util.import_script("ai_fields/saas~18.5.0.1/pre-migrate.py")


def migrate(cr, version):
    util.convert_field_to_html(cr, "ir.actions.server", "ai_prompt")

    cr.execute(
        """
        SELECT id, ai_prompt
          FROM ir_act_server
         WHERE ai_prompt IS NOT NULL
           AND (ai_prompt LIKE '%o_ai_field%' OR ai_prompt LIKE '%o_ai_record%')
        """,
    )
    for line in cr.dictfetchall():
        cr.execute(
            "UPDATE ir_act_server SET ai_prompt = %s WHERE id = %s",
            (ai_fields_18_pre_migrate.migrate_ai_prompt(line["ai_prompt"]), line["id"]),
        )

    util.rename_field(cr, "ir.actions.server", "ai_prompt", "ai_update_prompt")
