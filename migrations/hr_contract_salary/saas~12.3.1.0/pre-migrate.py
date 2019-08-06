# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_field(cr, 'hr.contract', 'active_employee')
    util.create_column(cr, 'hr_employee', 'id_card', 'bytea')
    util.create_column(cr, 'hr_employee', 'driving_license', 'bytea')
    util.create_column(cr, 'hr_employee', 'mobile_invoice', 'bytea')
    util.create_column(cr, 'hr_employee', 'sim_card', 'bytea')
    util.create_column(cr, 'hr_employee', 'internet_invoice', 'bytea')
