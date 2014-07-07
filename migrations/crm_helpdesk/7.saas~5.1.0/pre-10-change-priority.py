# -*- coding: utf-8 -*-
# Priority Mapping For crm.helpdesk
# Low, Lowest = Low
# Normal = Normal
# High, Highest = Highest

def migrate(cr, version):
	cr.execute("""UPDATE crm_helpdesk
			SET priority = CASE WHEN priority in ('5','4') THEN '0'
                            WHEN priority in ('3') THEN '1'
                            WHEN priority in ('2','1') THEN '2'
                            END
            WHERE priority IS NOT NULL""")
