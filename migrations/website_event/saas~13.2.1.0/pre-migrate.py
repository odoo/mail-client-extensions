# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "website_event.remove_external_snippets")
    util.remove_view(cr, "website_event.ticket")
