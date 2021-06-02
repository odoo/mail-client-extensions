# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "approval_approver", "required", "bool", default=False)

    util.create_column(cr, "approval_category", "manager_approval", "varchar")
    cr.execute("UPDATE approval_category SET manager_approval='approver' WHERE is_manager_approver=TRUE")
    util.remove_field(cr, "approval.request", "is_manager_approver")
    util.remove_field(cr, "approval.category", "is_manager_approver")
