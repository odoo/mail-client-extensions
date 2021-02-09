# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.merge_module(cr, "account_edi_extended", "account_edi", without_deps=True)
