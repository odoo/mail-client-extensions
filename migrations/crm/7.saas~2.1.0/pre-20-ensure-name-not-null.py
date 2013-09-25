# -*- coding: utf-8 -*-
def migrate(cr, version):
    cr.execute("UPDATE crm_lead SET name='Lead #' || id WHERE name IS NULL")
    cr.execute("UPDATE crm_phonecall SET name='Call ' || coalesce(partner_phone, '') WHERE name IS NULL")
