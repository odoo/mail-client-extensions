# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.create_column(cr, 'crm_team', 'company_id', 'int4')    # no default value

    cr.execute("ALTER TABLE crm_team ALTER COLUMN name TYPE varchar")   # no limit
    # no more hierarchy on crm.team
    cr.execute("""
        WITH RECURSIVE teams AS (
            SELECT id, name
              FROM crm_team
             WHERE parent_id IS NULL
             UNION
            SELECT c.id, concat(w.name, ' / ', c.name)
              FROM crm_team c
              JOIN teams w ON (c.parent_id = w.id)
        )
        UPDATE crm_team c
           SET name = w.name
          FROM teams w
         WHERE c.id = w.id
    """)
    util.remove_field(cr, 'crm.teams', 'parent_id')

    util.create_column(cr, 'res_users', 'sale_team_id', 'int4')
    # remove duplicates
    if util.table_exists(cr, 'crm_lead'):
        sub = """select team_id
                   from crm_lead
                  where team_id = any(dbl.teams)
                    and user_id = dbl.member_id
               order by create_date desc
                  limit 1"""
    else:
        sub = """SELECT max(team_id)
                   FROM sale_member_rel
                  WHERE member_id = dbl.member_id"""
    cr.execute("""
        WITH dbl AS (
            SELECT member_id, array_agg(team_id) as teams
              FROM sale_member_rel
          GROUP BY member_id
            HAVING count(*) > 1
        )
        DELETE from sale_member_rel r
         USING dbl
         WHERE r.member_id = dbl.member_id
           AND team_id != ({sub})
    """.format(sub=sub))

    cr.execute("""
        UPDATE res_users u
           SET sale_team_id=r.team_id
          FROM sale_member_rel r
         WHERE r.member_id = u.id
    """)

    cr.execute("DROP TABLE sale_member_rel")
