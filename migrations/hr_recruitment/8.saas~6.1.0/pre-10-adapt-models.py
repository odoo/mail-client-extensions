# -*- coding: utf-8 -*-
from operator import itemgetter
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):

    # some source have been created via xml file. Keep only the one used in applicants
    xids = "source_linkedin source_monster source_word source_website_company".split()
    cr.execute("""DELETE FROM ir_model_data d
                        WHERE module=%s
                          AND name IN %s
                          AND NOT EXISTS(SELECT 1
                                           FROM hr_applicant
                                          WHERE source_id=d.res_id)
                    RETURNING res_id
               """, ['hr_recruitment', tuple(xids)])
    unused_sources = map(itemgetter(0), cr.fetchall())
    cr.execute("DELETE FROM hr_recruitment_source WHERE id=ANY(%s)", [unused_sources])

    util.create_column(cr, 'hr_recruitment_source', 'source_id', 'int4')

    # have to be done in 2 query. Update of utm_souce.name cannot be done in the CTE as it does
    # not have knowledge of just inserted rows we try updating
    cr.execute("""
        WITH s AS (SELECT id FROM hr_recruitment_source),
             i AS (INSERT INTO utm_source(name) SELECT id::varchar FROM s RETURNING id, name),
             u AS (UPDATE hr_recruitment_source r
                      SET source_id=i.id
                     FROM i
                    WHERE r.id=i.name::int4)
      SELECT 1
    """)
    cr.execute("""UPDATE utm_source x
                     SET name=u.name
                    FROM hr_recruitment_source u
                   WHERE x.id=u.source_id
               """)

    # hr_applicant.source_id now point to a utm_source (through utm.mixin)
    cr.execute("ALTER TABLE hr_applicant DROP CONSTRAINT hr_applicant_source_id_fkey")
    cr.execute("""UPDATE hr_applicant a
                     SET source_id=s.source_id
                    FROM hr_recruitment_source s
                   WHERE a.source_id = s.id
               """)
