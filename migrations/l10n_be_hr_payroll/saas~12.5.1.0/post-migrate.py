# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.recompute_fields(cr, "hr.payslip", ["has_attachment_salary"])
