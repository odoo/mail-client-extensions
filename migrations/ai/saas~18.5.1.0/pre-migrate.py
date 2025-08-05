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

    # Delete records without embedding_vector. No assigned vector means the embedding
    # record hasn't been sent to the OpenAI API yet. These records can be deleted.
    delete_query = """
        DELETE FROM ai_embedding
              WHERE embedding_vector IS NULL
    """
    util.explode_execute(cr, delete_query, table="ai_embedding")

    # Each ai.embedding record prior to https://github.com/odoo/enterprise/pull/84756
    # was created via the OpenAI embedding model "text-embedding-3-small".
    util.create_column(cr, "ai_embedding", "embedding_model", "varchar", default="text-embedding-3-small")
