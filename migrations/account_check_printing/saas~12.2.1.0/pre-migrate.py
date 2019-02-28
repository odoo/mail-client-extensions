# -*- coding: utf-8 -*-


def migrate(cr, version):
    cr.execute("ALTER TABLE account_register_payments ALTER COLUMN check_number TYPE varchar")
    cr.execute("ALTER TABLE account_payment ALTER COLUMN check_number TYPE varchar")
    cr.execute("ALTER TABLE print_prenumbered_checks ALTER COLUMN next_check_number TYPE varchar")
