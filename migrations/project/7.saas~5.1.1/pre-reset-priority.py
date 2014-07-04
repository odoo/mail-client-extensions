# -*- coding: utf-8 -*-
def migrate(cr, version):

    #    saas-4              saas-5
    #    ====                ====
    #    Very Low            Low
    #    Low                 Low
    #    Medium              Normal
    #    Very important      High
    #    important           High

    cr.execute("""UPDATE project_task
                    SET priority = CASE WHEN priority in ('4','3') THEN '0'
                                    WHEN priority in ('2') THEN '1'
                                    WHEN priority in ('1','0') THEN '2'
                                    END
                    WHERE priority IS NOT NULL 
    """)
