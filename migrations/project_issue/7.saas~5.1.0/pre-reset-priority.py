# -*- coding: utf-8 -*-
def migrate(cr, version):

    #   saas-4       saas-5
    #   ======       ======
    #   Lowest       Low
    #   Low          Low
    #   Normal       Normal
    #   High         High
    #   Highest      High

    cr.execute("""UPDATE project_issue
                    SET priority = CASE WHEN priority in ('5','4') THEN '0'
                                    WHEN priority in ('3') THEN '1'
                                    WHEN priority in ('2','1') THEN '2'
                                    END
                    WHERE priority IS NOT NULL 
    """)
