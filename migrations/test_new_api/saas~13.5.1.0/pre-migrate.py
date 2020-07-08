# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.rename_model(cr, "test_new_api.compute.protected", "test_new_api.compute.readonly")
    util.rename_xmlid(
        cr, "test_new_api.access_test_new_api_compute_protected", "test_new_api.access_test_new_api_compute_readonly"
    )
