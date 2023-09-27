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
