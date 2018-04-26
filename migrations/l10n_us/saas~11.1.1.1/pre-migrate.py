# -*- coding: utf-8 -*-

def migrate(cr, version):
    cr.execute("ALTER TABLE res_partner_bank ALTER COLUMN aba_routing TYPE varchar")
