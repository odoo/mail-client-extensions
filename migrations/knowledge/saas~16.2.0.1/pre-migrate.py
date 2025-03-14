from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "knowledge_article", "is_article_visible_by_everyone", "boolean", default=False)
    cr.execute(
        """
        UPDATE knowledge_article
           SET is_article_visible_by_everyone = True
         WHERE category = 'workspace'
        """
    )
