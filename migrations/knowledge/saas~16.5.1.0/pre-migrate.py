# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "knowledge.knowledge_embedded_view")
    util.remove_view(cr, "knowledge.knowledge_view_link")
