# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    # When nothing else other than web is installed this "asset" is never called
    # with t-call-assets, so it passes between the net's mesh
    util.remove_view(cr, "web.pdf_js_lib")
