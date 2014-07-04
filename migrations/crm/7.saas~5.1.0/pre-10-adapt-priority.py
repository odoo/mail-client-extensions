# -*- coding: utf-8 -*-
def migrate(cr, version):
    # Reverse priority values in crm.lead
    cr.execute("UPDATE crm_lead SET priority=abs(priority::int - 5)::varchar")

    # Priority mapping for crm.phonecall
    # High, Highest > Highest
    # Normal > Normal
    # Low, Lowest > Low
    cr.execute("""UPDATE crm_phonecall SET priority = CASE
                WHEN priority in ('1','2') THEN '2'
                WHEN priority = '3' THEN '1'
                WHEN priority in ('4','5') THEN '0' END""")
