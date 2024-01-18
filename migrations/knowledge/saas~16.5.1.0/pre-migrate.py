# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "knowledge.knowledge_embedded_view")
    util.remove_view(cr, "knowledge.knowledge_view_link")
    util.remove_view(cr, "knowledge.knowledge_article_tree_favorites")
    util.remove_view(cr, "knowledge.knowledge_article_tree_frontend")
    if util.module_installed(cr, "website_knowledge"):
        util.rename_xmlid(cr, "knowledge.layout", "website_knowledge.layout")
        util.rename_xmlid(cr, "knowledge.articles_template", "website_knowledge.articles_template")
        util.rename_xmlid(cr, "knowledge.knowledge_article_view_frontend", "website_knowledge.article_view_public")
    else:
        util.remove_view(cr, "knowledge.layout")
        util.remove_view(cr, "knowledge.articles_template")
        util.remove_view(cr, "knowledge.knowledge_article_view_frontend")

    # rename view_in_kanban to view_in_cards in properties definition
    cr.execute(
        """
        UPDATE knowledge_article
           SET article_properties_definition = (
                SELECT jsonb_agg(
                  CASE WHEN definition ? 'view_in_kanban' THEN jsonb_set(definition - 'view_in_kanban', '{view_in_cards}', definition->'view_in_kanban', true)
                       ELSE definition
                   END
            )     FROM jsonb_array_elements(article_properties_definition) AS definition
        );
        """
    )

    util.remove_field(cr, "knowledge.cover", "article_template_ids")

    util.create_column(cr, "knowledge_article", "is_template", "bool")
    util.create_column(cr, "knowledge_article", "template_body", "jsonb")
    kw = (
        {"fk_table": "knowledge_article_template_category", "on_delete_action": "SET NULL"}
        if util.table_exists(cr, "knowledge_article_template_category")
        else {}
    )
    util.create_column(
        cr,
        "knowledge_article",
        "template_category_id",
        "int4",
        **kw,
    )
    util.create_column(cr, "knowledge_article", "template_description", "jsonb")
    util.create_column(cr, "knowledge_article", "template_name", "jsonb")
    util.create_column(cr, "knowledge_article", "template_sequence", "int4")

    if util.table_exists(cr, "knowledge_article_template"):
        util.create_column(cr, "knowledge_article", "_upg_template_id", "int4")
        util.create_column(cr, "knowledge_article", "_upg_template_parent_id", "int4")

        cr.execute(
            """
            INSERT INTO knowledge_article (
                active,
                article_properties,
                article_properties_definition,
                cover_image_id,
                create_date,
                create_uid,
                full_width,
                icon,
                internal_permission,
                is_article_item,
                is_template,
                template_body,
                template_category_id,
                template_description,
                template_name,
                template_sequence,
                _upg_template_id,
                _upg_template_parent_id,
                write_date,
                write_uid
            )
            SELECT
                TRUE                           AS active,
                template_properties            AS article_properties,
                template_properties_definition AS article_properties_definition,
                cover_image_id,
                create_date,
                create_uid,
                FALSE                          AS full_width,
                icon,
                'write'                        AS internal_permission,
                is_template_item               AS is_article_item,
                TRUE                           AS is_template,
                body                           AS template_body,
                category_id                    AS template_category,
                description                    AS template_description,
                name                           AS template_name,
                sequence                       AS template_sequence,
                id                             AS _upg_template_id,
                parent_id                      AS _upg_template_parent_id,
                write_date,
                write_uid
            FROM knowledge_article_template
       RETURNING _upg_template_id, id;
        """
        )
        mapping = dict(cr.fetchall())
        if mapping:
            util.replace_record_references_batch(
                cr, mapping, model_src="knowledge.article.template", model_dst="knowledge.article"
            )

        cr.execute(
            """
            UPDATE knowledge_article AS child
               SET parent_id = parent.id
              FROM knowledge_article AS parent
             WHERE child._upg_template_parent_id = parent._upg_template_id;
            """
        )

        util.remove_column(cr, "knowledge_article", "_upg_template_id")
        util.remove_column(cr, "knowledge_article", "_upg_template_parent_id")

        util.merge_model(
            cr,
            "knowledge.article.template",
            "knowledge.article",
            fields_mapping={
                "body": "template_body",
                "category_id": "template_category_id",
                "description": "template_description",
                "name": "template_name",
                "sequence": "template_sequence",
                "template_properties": "article_properties",
                "template_properties_definition": "article_properties_definition",
            },
        )
