# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "hr.expense", "extract_can_show_resend_button")

    util.remove_field(cr, "hr.expense", "extract_word_ids")
    util.remove_model(cr, "hr.expense.extract.words")
