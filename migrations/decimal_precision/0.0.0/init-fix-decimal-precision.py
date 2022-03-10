# -*- coding: utf-8 -*-


def prepare_migration(cr):
    cr.execute(
        """
        SELECT 1
          FROM information_schema.columns
         WHERE table_name='decimal_precision'
           AND column_name='display_digits'
        """
    )
    if cr.rowcount:
        cr.execute("ALTER TABLE decimal_precision ALTER display_digits DROP NOT NULL")
