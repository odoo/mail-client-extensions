# -*- coding: utf-8 -*-


def migrate(cr, version):
    cr.execute("ALTER TABLE hr_expense_sheet_register_payment_wizard ALTER COLUMN check_number TYPE varchar")
