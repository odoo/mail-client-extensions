# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # reset shared source_id
    cr.execute(
        """
        WITH ss AS (
            SELECT unnest(array_agg(id)) as id
              FROM mail_mass_mailing
             WHERE source_id IS NOT NULL
          GROUP BY source_id
            HAVING count(*) > 1
        )
        UPDATE mail_mass_mailing m
           SET source_id=NULL
          FROM ss
         WHERE m.id = ss.id
    """
    )

    # NOTE: UNION act as a GROUP BY source_id
    used_sources = " UNION ".join(
        "SELECT {1} AS source_id FROM {0} WHERE {1} IS NOT NULL".format(tbl, col)
        for tbl, col, _, _ in util.get_fk(cr, "utm_source")
        if tbl != "mail_mass_mailing"
    )
    if used_sources:
        used_sources += " UNION "
    used_sources += """
        SELECT res_id
          FROM ir_model_data
         WHERE model = 'utm.source'
           AND COALESCE(module, '') NOT IN ('', '__export__')
    """

    cr.execute("UPDATE mail_mass_mailing SET source_id=NULL WHERE source_id IN ({0})".format(used_sources))

    # have to be done in 2 query. Update of utm_souce.name cannot be done in the CTE as it does
    # not have knowledge of just inserted rows we try updating
    cr.execute(
        """
        WITH s AS (SELECT id FROM mail_mass_mailing WHERE source_id IS NULL),
             i AS (INSERT INTO utm_source(name) SELECT id::varchar FROM s RETURNING id, name),
             u AS (UPDATE mail_mass_mailing m
                      SET source_id=i.id
                     FROM i
                    WHERE m.id=i.name::int4)
      SELECT 1
    """
    )

    cr.execute(
        """
        UPDATE utm_source s
           SET name = m.name,
               write_date = now() at time zone 'utc'
          FROM mail_mass_mailing m
         WHERE m.source_id = s.id
           AND COALESCE(m.write_date, m.create_date) >= COALESCE(s.write_date, s.create_date, '-infinity')
    """
    )
