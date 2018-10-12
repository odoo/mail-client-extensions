# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "payment_acquirer", "website_id", "int4")
    util.remove_view(cr, "website_payment.website_settings_payment")
