#!/usr/bin/env python
# -*- coding: utf-8 -*-

def migrate(cr, version):
    """remove empty string default values. This behavior cannot be reproduced via the ORM"""

    cr.execute("""SELECT quote_ident(table_name), quote_ident(column_name)
                    FROM information_schema.columns
                   WHERE column_default = %s
               """, ("''::character varying",))

    for table, column in cr.fetchall():
        cr.execute("ALTER TABLE {0} ALTER COLUMN {1} DROP DEFAULT".format(table, column))
        cr.execute("UPDATE {0} SET {1}=NULL WHERE {1}=''".format(table, column))
