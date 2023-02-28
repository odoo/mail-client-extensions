# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_model(cr, "account.link.journal.line")
    util.remove_model(cr, "account.link.journal")
    util.create_column(cr, "account_journal", "renewal_contact_email", "varchar")
