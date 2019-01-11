# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.if_unchanged(cr, "hr.mail_template_data_unknown_employee_email_address", util.update_record_from_xml)
