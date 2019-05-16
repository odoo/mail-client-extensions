# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.convert_binary_field_to_attachment(cr, "slide.slide", "datas")  # seriously?
