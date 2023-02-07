# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    # Wizard account.invoice.send replaced by account.move.send
    util.remove_model(cr, "snailmail.confirm.invoice")
