# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_field(cr, "followup.send", "letter_ids")
    util.remove_field(cr, "followup.send", "currency_id")
