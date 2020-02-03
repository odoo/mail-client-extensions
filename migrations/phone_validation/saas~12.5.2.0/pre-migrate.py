# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_field(cr, "res.company", "phone_international_format")
    util.remove_view(cr, "phone_validation.res_company_view_form_phone_validation")
