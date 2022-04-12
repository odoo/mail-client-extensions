# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):

    if util.has_enterprise():
        util.merge_module(cr, "documents_spreadsheet_bundle", "documents_spreadsheet")
