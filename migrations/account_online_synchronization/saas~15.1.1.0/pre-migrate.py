# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "account.link.journal.line", "action")
    util.remove_field(cr, "account.link.journal.line", "journal_statements_creation")
