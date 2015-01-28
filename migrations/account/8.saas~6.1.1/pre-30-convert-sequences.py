# -*- coding: utf-8 -*-
import datetime
from openerp import SUPERUSER_ID
from openerp.addons.base.maintenance.migrations import util
from openerp.modules.registry import RegistryManager
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT

def migrate(cr, version):
    # synchronize `number_next` for `standard` sequences.
    # as a sub-sequence can be `standard` while the main sequence is `no-gap` (that's a
    # configuration error that will be auto-corrected, but it can't rewind the sequence
    # when updating)
    # NOTE using the orm is correct as the model `ir.sequence` is already loaded
    registry = RegistryManager.get(cr.dbname)
    Seq = registry['ir.sequence']
    ctx = dict(active_test=False)
    ids = Seq.search(cr, SUPERUSER_ID, [('implementation', '=', 'standard')], context=ctx)
    for s in Seq.browse(cr, SUPERUSER_ID, ids):
        # use a query to not change write_uid / write_date
        cr.execute("UPDATE ir_sequence SET number_next=%s WHERE id=%s",
                   [s.number_next_actual or 1, s.id])

    cr.execute("""SELECT a.id, a.sequence_main_id, a.sequence_id,
                         s.implementation, s.number_next,
                         f.date_start, f.date_stop
                    FROM account_sequence_fiscalyear a
              INNER JOIN account_fiscalyear f
                      ON f.id = a.fiscalyear_id
              INNER JOIN ir_sequence s
                      ON s.id = a.sequence_id
               """)
    for asf_id, main_seq_id, seq_id, impl, number_next, date_start, date_stop in cr.fetchall():
        cr.execute("""INSERT INTO ir_sequence_date_range
                                  (sequence_id, number_next, date_from, date_to)
                           VALUES (%s, %s, %s, %s)
                        RETURNING id
                   """, [main_seq_id, number_next, date_start, date_stop])
        [dr_id] = cr.fetchone()
        if impl == 'standard':
            cr.execute("ALTER SEQUENCE ir_sequence_%03d RENAME TO ir_sequence_%03d_%03d" %
                       (seq_id, main_seq_id, dr_id))

        cr.execute("UPDATE ir_sequence SET use_date_range=true, active=true WHERE id=%s", [main_seq_id])

        dt_start = datetime.datetime.strptime(date_start, DEFAULT_SERVER_DATE_FORMAT)
        dt_stop = datetime.datetime.strptime(date_stop, DEFAULT_SERVER_DATE_FORMAT)
        if dt_start <= datetime.datetime.utcnow() <= dt_stop:
            cr.execute("""UPDATE ir_sequence m
                             SET prefix=replace(s.prefix, date_part('year', now())::varchar, '%%(year)s'),
                                 suffix=replace(s.suffix, date_part('year', now())::varchar, '%%(year)s'),
                                 padding=s.padding
                            FROM ir_sequence s
                           WHERE m.id = %s
                             AND s.id = %s
                       """, [main_seq_id, seq_id])

        # we need to delete the record ourself to avoid integrity constraint violation
        cr.execute("DELETE FROM account_sequence_fiscalyear WHERE id=%s", [asf_id])
        util.replace_record_references(cr, ('ir.sequence', seq_id), ('ir.sequence', main_seq_id))
        cr.execute("DELETE FROM ir_sequence WHERE id=%s", [seq_id])

    util.delete_model(cr, 'account.sequence.fiscalyear')
