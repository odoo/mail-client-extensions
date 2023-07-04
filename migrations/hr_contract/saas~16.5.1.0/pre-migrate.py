# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.update_field_usage(cr, "hr.contract", "visa_expire", "employee_id.work_permit_expiration_date")
    util.remove_field(cr, "hr.contract", "visa_expire")
