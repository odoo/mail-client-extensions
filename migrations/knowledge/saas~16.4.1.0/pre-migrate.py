# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "knowledge.articles_template_name")
    util.remove_view(cr, "knowledge.knowledge_article_tree")
