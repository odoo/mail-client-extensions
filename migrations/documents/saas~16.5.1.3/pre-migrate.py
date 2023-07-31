# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "documents.share_single")
    util.remove_view(cr, "documents.share_page")
