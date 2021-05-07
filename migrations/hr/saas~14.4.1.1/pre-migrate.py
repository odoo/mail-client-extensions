# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "hr_employee", "work_permit_scheduled_activity", "boolean", default=False)
    util.create_column(cr, "hr_employee", "work_permit_expiration_date", "date")
    util.convert_field_to_html(cr, "hr.job", "description")
