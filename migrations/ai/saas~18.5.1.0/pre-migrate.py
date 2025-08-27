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
                WHEN 'Mail/Note Composer' THEN 'mail_composer'
                WHEN 'Record HTML Fields' THEN 'html_field_record'
                WHEN 'Text Selector' THEN 'html_field_text_select'
                WHEN 'Chatter Helper' THEN 'chatter_ai_button'
                WHEN 'Mail Template Prompt Evaluator' THEN 'html_prompt_shortcut'
                ELSE 'mail_composer'
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

    # name of ai_topic and ai_composer are now required
    cr.execute("""
        UPDATE ai_composer
           SET name = 'Composer #' || id
         WHERE name IS NULL
    """)
    cr.execute("""
        UPDATE ai_topic
           SET name = 'Topic #' || id
         WHERE name IS NULL
    """)

    eb = util.expand_braces
    # ai/views/ai_menus.xml
    util.rename_xmlid(cr, *eb("ai{,_app}.ai_menu_root"))
    util.rename_xmlid(cr, *eb("ai{,_app}.ai_menu"))
    util.rename_xmlid(cr, *eb("ai{,_app}.ai_agent_menu_action"))
    util.rename_xmlid(cr, *eb("ai{,_app}.ai_topic_menu_action"))
    util.rename_xmlid(cr, *eb("ai{,_app}.ai_config_menu"))
    util.rename_xmlid(cr, *eb("ai{,_app}.ai_general_settings_menu"))
    util.rename_xmlid(cr, *eb("ai{,_app}.menu_ai_composer"))
    # ai/views/res_config_settings_views.xml
    util.rename_xmlid(cr, *eb("ai{,_app}.ai_settings_action"))
    # ai/views/ai_agent_views.xml
    util.rename_xmlid(cr, *eb("ai{,_app}.ai_agent_view_kanban"))
    util.rename_xmlid(cr, *eb("ai{,_app}.ai_agent_view_tree"))
    util.rename_xmlid(cr, *eb("ai{,_app}.ai_agent_view_form"))
    util.rename_xmlid(cr, *eb("ai{,_app}.ai_agent_view_search"))
    util.rename_xmlid(cr, *eb("ai{,_app}.ai_agent_action"))
    # ai/views/ai_topic_views.xml
    util.rename_xmlid(cr, *eb("ai{,_app}.ai_topic_view_search"))
    util.rename_xmlid(cr, *eb("ai{,_app}.ai_topic_view_form"))
    util.rename_xmlid(cr, *eb("ai{,_app}.ai_topic_view_list"))
    util.rename_xmlid(cr, *eb("ai{,_app}.ai_topic_view_kanban"))
    util.rename_xmlid(cr, *eb("ai{,_app}.ai_topic_action"))
    # ai/views/ai_composer_views.xml
    util.rename_xmlid(cr, *eb("ai{,_app}.ai_composer_form"))
    util.rename_xmlid(cr, *eb("ai{,_app}.ai_composer_tree"))
    util.rename_xmlid(cr, *eb("ai{,_app}.ai_composer_kanban"))
    util.rename_xmlid(cr, *eb("ai{,_app}.ai_composer_action"))
