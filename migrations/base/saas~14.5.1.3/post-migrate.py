# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(cr, "base.paperformat_batch_deposit", util.update_record_from_xml)
