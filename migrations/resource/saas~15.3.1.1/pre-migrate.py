# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    # The model is moved into a new module test_resource
    # But this is actually a "test" model, and no record
    # should be migrated.
    util.remove_model(cr, "resource.test")
