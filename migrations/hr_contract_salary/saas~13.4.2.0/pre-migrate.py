# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "hr.contract", "access_token")
    util.remove_field(cr, "hr.contract", "access_token_consumed")
    util.remove_field(cr, "hr.contract", "access_token_end_date")

    util.create_column(cr, "hr_contract", "hash_token", "varchar")
