# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_view(cr, "base.user_groups_view")
    util.remove_record(cr, "base.access_ir_attachment_all")
    util.remove_record(cr, "base.access_ir_attachment_portal")
