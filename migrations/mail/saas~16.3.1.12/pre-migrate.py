# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    # Remove old discuss public view
    util.remove_view(cr, "mail.discuss_public_layout")
