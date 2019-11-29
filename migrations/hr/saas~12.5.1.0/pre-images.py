# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    image = util.import_script("base/saas~12.5.1.3/pre-21-images.py")
    image.new_inherit_mixin(cr, "hr.employee")
    image.new_inherit_mixin(cr, "hr.employee.public")
