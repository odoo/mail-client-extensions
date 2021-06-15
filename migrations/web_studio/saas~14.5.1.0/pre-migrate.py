# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "web_studio.qunit_suite")
    util.remove_view(cr, "web_studio.webclient_bootstrap")
