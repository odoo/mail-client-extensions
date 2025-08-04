from odoo.upgrade import util


def migrate(cr, version):
    # The ai_tool model has been refactored. The old records don't follow the new logic.
    # These records will be dropped and new records will be registered following the new logic.
    cr.execute("SELECT server_action FROM ai_tool WHERE server_action IS NOT NULL")
    sids = [sid for (sid,) in cr.fetchall()]

    if sids:
        util.remove_records(cr, "ir.actions.server", sids)

    util.remove_model(cr, "ai.tool")
    util.remove_field(cr, "discuss.channel", "ai_composer")
    util.remove_field(cr, "discuss.channel", "ai_context")

    util.create_column(cr, "ai_composer", "interface_key", "varchar")
    # interface key is a required field
    cr.execute("""
        UPDATE ai_composer composer
           SET interface_key =
            CASE composer.name
                WHEN 'Mail/Note Composer' THEN 'composer_ai_button'
                WHEN 'Record HTML Fields' THEN 'html_field_record'
                WHEN 'Text Selector' THEN 'html_field_text_select'
                WHEN 'Chatter Helper' THEN 'chatter_ai_button'
                WHEN 'Mail Template Prompt Evaluator' THEN 'html_prompt_shortcut'
                ELSE 'composer_ai_button'
            END
    """)
