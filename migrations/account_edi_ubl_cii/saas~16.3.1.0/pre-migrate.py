# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "account_edi_ubl_cii.view_account_journal_form_inherited")
