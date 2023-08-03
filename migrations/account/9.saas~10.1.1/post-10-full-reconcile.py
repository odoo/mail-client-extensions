# -*- coding: utf-8 -*-
from collections import OrderedDict
import datetime
import json
import logging
from openerp.addons.base.maintenance.migrations import util
from openerp.tools import float_compare
from psycopg2.extras import execute_values
from openerp import SUPERUSER_ID

_logger = logging.getLogger(__name__)

def migrate(cr, version):
    # avoid doing anything if the table has already something in it (already migrated)
    cr.execute("SELECT count(id) FROM account_full_reconcile")
    res = cr.fetchone()[0]
    if res:
        return

    # check column reconcile_id exists on account.move.line
    cr.execute("""
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'account_move_line'
          AND column_name = 'reconcile_id'
        """)
    if cr.fetchone():
        # if yes, use the table account_move_reconcile if it exists (not dropped by migration)
        cr.execute("SELECT 1 FROM information_schema.tables WHERE table_name = 'account_move_reconcile'")
        if cr.fetchone():
            # account_move_reconcile exists
            # copy old table
            cr.execute("""
                INSERT INTO account_full_reconcile (id, name, create_date)
                    SELECT id, name, create_date
                    FROM account_move_reconcile
                    WHERE id IN (
                        SELECT DISTINCT reconcile_id FROM account_move_line WHERE reconcile_id IS NOT NULL)
                """)
        else:
            # account_move_reconcile was dropped during migration, rebuild that table
            cr.execute("""
                INSERT INTO account_full_reconcile (id, name)
                    SELECT DISTINCT reconcile_id, reconcile_ref FROM account_move_line WHERE reconcile_id IS NOT NULL
                """)
        # update the index of account_full_reconcile
        cr.execute("SELECT setval('account_full_reconcile_id_seq', (SELECT MAX(id) FROM account_full_reconcile))")

        # copy the full_reconcile_id existing of account.move.line to their account.partial.reconcile
        cr.execute("""
            WITH tmp_table AS (
              SELECT partial_id, MAX(full_id) AS full_id FROM (
                SELECT rec.id AS partial_id, aml.reconcile_id AS full_id
                FROM account_move_line aml
                RIGHT JOIN account_partial_reconcile rec
                    ON aml.id = rec.debit_move_id
                WHERE aml.reconcile_id IS NOT NULL
                UNION
                SELECT rec.id AS partial_id, aml.reconcile_id AS full_id
                FROM account_move_line aml
                RIGHT JOIN account_partial_reconcile rec
                    ON aml.id = rec.credit_move_id
                WHERE aml.reconcile_id IS NOT NULL) tmp_table_with_duplicated_recs
             GROUP BY partial_id HAVING COUNT(partial_id) = 1)
            UPDATE account_partial_reconcile p
            SET full_reconcile_id = tmp.full_id FROM tmp_table tmp WHERE p.id = tmp.partial_id
            """)
    # if it's a fresh v9 database, or it has been used after the migration, we need to fill the table based on partial
    env = util.env(cr)
    all_partial_rec_ids = env['account.partial.reconcile'].search([('full_reconcile_id', '=', False)]).ids
    already_processed = {}
    batch_create = []  # list of account.partial.reconcile ids that map into _one_ full reconcile
    for partial in util.iter_browse(env['account.partial.reconcile'], all_partial_rec_ids, logger=_logger):
        partial_rec_set = OrderedDict.fromkeys([partial])
        aml_set = set()
        total_debit = 0
        total_credit = 0
        for partial_rec in partial_rec_set:
            if partial_rec in already_processed:
                continue
            for aml in [partial_rec.debit_move_id, partial_rec.credit_move_id]:
                if aml not in aml_set:
                    total_debit += aml.debit
                    total_credit += aml.credit
                    aml_set |= set([aml])
                for x in aml.matched_debit_ids | aml.matched_credit_ids:
                    partial_rec_set[x] = None
        partial_rec_ids = []
        for x in partial_rec_set.keys():
            partial_rec_ids.append(x.id)
            already_processed[x] = None
        aml_ids = [x.id for x in aml_set]
        if aml_ids and partial_rec_ids:
            # then, if the total debit and credit are equal, the reconciliation is full
            digits_rounding_precision = aml.company_id.currency_id.rounding
            if float_compare(total_debit, total_credit, precision_rounding=digits_rounding_precision) == 0:
                # in that case, mark the reference on the partial reconciliations and the entries
                # batch_create.append({'partial_reconcile_ids': [(6, 0, partial_rec_ids)]})
                batch_create.append(partial_rec_ids)

    if batch_create:
        _logger.info("Create account.full.reconcile records")
        chunk_size = 1000
        now = datetime.datetime.utcnow()
        seq = env['ir.sequence'].search([("code", "=", "account.reconcile")])
        size = (len(batch_create) - 1) / chunk_size + 1

        for chunk in util.log_progress(
            util.chunks(batch_create, chunk_size, fmt=list),
            _logger,
            size=size,
            qualifier="chunks of {} records".format(chunk_size),
        ):
            cr.execute(
                """
                INSERT INTO account_full_reconcile(name, write_date, create_date, create_uid, write_uid)
                     VALUES {}
                  RETURNING id
                """.format(
                    ",".join(
                        cr.mogrify("(%s,%s,%s,%s,%s)", [seq._next(), now, now, SUPERUSER_ID, SUPERUSER_ID]).decode()
                        for _ in chunk
                    )
                )
            )
            afr_ids = [r[0] for r in cr.fetchall()]
            new_ids = {apr_id: afr_id for apr_ids, afr_id in zip(chunk, afr_ids) for apr_id in apr_ids}
            cr.execute(
                """
                UPDATE account_partial_reconcile
                   SET full_reconcile_id = (%s::jsonb->>(id::text))::int
                 WHERE id IN %s
                """,
                [json.dumps(new_ids), tuple(new_ids)]
            )

    # copy values on account.move.line: rely on partial reconciliations only, as the reconcile_id column may not be
    # up-to-date, as unreconciliations/new reconciliations may have been done after migration
    cr.execute("""
        WITH tmp_table AS (
            SELECT debit_move_id AS aml_id, full_reconcile_id
            FROM account_partial_reconcile rec
            WHERE rec.full_reconcile_id IS NOT NULL
            UNION ALL
            SELECT credit_move_id AS aml_id, full_reconcile_id
            FROM account_partial_reconcile rec
            WHERE rec.full_reconcile_id IS NOT NULL)
        UPDATE account_move_line aml
        SET full_reconcile_id = tmp.full_reconcile_id FROM tmp_table tmp WHERE aml.id = tmp.aml_id
    """)
