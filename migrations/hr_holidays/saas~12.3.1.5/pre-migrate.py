# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    eb = util.expand_braces
    util.create_column(cr, "hr_leave_type", 'responsible_id', 'int4')
    util.rename_xmlid(cr, *eb("hr_holidays.{h,}hr_leave_action_new_request_view_form"))
