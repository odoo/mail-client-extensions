from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "website_knowledge.articles_template")
    util.remove_view(cr, "website_knowledge.public_sidebar")
