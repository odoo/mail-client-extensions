def migrate(cr, version):
    cr.execute(
        """
        UPDATE hr_leave_allocation
           SET actual_lastcall = lastcall
         WHERE actual_lastcall IS NULL
           AND lastcall IS NOT NULL
           AND allocation_type = 'accrual'
         """
    )
