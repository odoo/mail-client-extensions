# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):

    util.remove_model(cr, "base_import.tests.models.char")
    util.remove_model(cr, "base_import.tests.models.char.required")
    util.remove_model(cr, "base_import.tests.models.char.readonly")
    util.remove_model(cr, "base_import.tests.models.char.states")
    util.remove_model(cr, "base_import.tests.models.char.noreadonly")
    util.remove_model(cr, "base_import.tests.models.char.stillreadonly")
    util.remove_model(cr, "base_import.tests.models.m2o")
    util.remove_model(cr, "base_import.tests.models.m2o.related")
    util.remove_model(cr, "base_import.tests.models.m2o.required")
    util.remove_model(cr, "base_import.tests.models.m2o.required.related")
    util.remove_model(cr, "base_import.tests.models.o2m")
    util.remove_model(cr, "base_import.tests.models.o2m.child")
    util.remove_model(cr, "base_import.tests.models.preview")
    util.remove_model(cr, "base_import.tests.models.float")
    util.remove_model(cr, "base_import.tests.models.complex")
