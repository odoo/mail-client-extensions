# -*- coding: utf-8 -*-

def migrate(cr, version):
    """ 
        Reset the priority field of hr_applicant with following mapping
        Saas4            Saas5
        -------------------------
        Not Good   ->     Bad
        On Average ->     Average
        Good       ->     Good
        Very Good  ->     Good
        Excellent  ->     Excellent
        
    """
    
    cr.execute("""UPDATE hr_applicant
                    SET priority = CASE WHEN priority in ('3','2') THEN '3'
                                    WHEN priority in ('5') THEN '0'
                                    WHEN priority in ('4') THEN '2'
                                    WHEN priority IN ('1') THEN '4'
                                    END
                    WHERE priority IS NOT NULL """)