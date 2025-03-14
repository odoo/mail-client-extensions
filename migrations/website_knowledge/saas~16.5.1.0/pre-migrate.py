from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "website_knowledge.website_knowledge_article_tree_frontend")
