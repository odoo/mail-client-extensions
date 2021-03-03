# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # Since odoo/odoo@ec162dd0cb5622ab6e56db1a63dab5f531a96f4a,the m2m tables
    # have a composite PK.
    # 5dedb04c6ae1f226c69bd498e88660d2601e305e adapt the code that create/fix
    # the m2m but it needs to be called explicitly.
    # In order to use logical replication in postgresql, all regular tables
    # needs a primary key (hence the initial commit).
    # Force this composite PK on all m2m tables.
    query = """
        SELECT c.relname, array_agg(a.attname order by a.attname)
          FROM pg_class c
          JOIN pg_namespace ns on ns.oid = c.relnamespace
     LEFT JOIN pg_constraint p on p.conrelid = c.oid and p.contype = 'p'
          JOIN pg_attribute a ON a.attrelid = c.oid and a.attnum > 0
         WHERE c.relkind IN ('r', 'p')
           AND ns.nspname = 'public'
           AND p.oid IS NULL
      GROUP BY c.relname
        HAVING count(a.attname) = 2
    """

    cr.execute(query)
    for m2m, columns in cr.fetchall():
        util.fixup_m2m_indexes(cr, m2m, *columns)
