# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "web.css_tests_assets")
    util.remove_view(cr, "web.js_tests_assets")

    # actually still there, but should be force-refresh
    # and indirectly remove inherited views
    util.remove_view(cr, "web.qunit_suite")
    util.remove_view(cr, "web.qunit_mobile_suite")
