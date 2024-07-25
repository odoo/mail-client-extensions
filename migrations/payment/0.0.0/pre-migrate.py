# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if util.version_between("17.0", "saas~17.5"):
        util.delete_unused(cr, "payment.payment_method_acss_debit")
