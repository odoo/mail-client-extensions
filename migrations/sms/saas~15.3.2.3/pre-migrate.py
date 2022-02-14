# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_model(cr, "sms.cancel", drop_table=True)

    util.remove_field(cr, "sms.composer", "active_domain")
    util.remove_field(cr, "sms.composer", "active_domain_count")
    util.remove_field(cr, "sms.composer", "use_active_domain")
