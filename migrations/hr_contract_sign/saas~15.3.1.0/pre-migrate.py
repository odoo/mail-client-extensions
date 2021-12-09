# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.rename_field(cr, "hr.contract.sign.document.wizard", "follower_ids", "cc_partner_ids")
