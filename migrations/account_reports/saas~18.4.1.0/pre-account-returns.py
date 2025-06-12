from psycopg2.extras import Json

from odoo.tools import html2plaintext

from odoo.upgrade import util


def migrate(cr, version):
    if not util.table_exists(cr, "account_return_check"):
        return

    util.remove_field(cr, "account.return.check", "summary")

    with util.named_cursor(cr) as ncr:
        ncr.execute("SELECT id, message FROM account_return_check WHERE message IS NOT NULL")

        data = ncr.fetchmany(1000)
        if ncr.rowcount == 1000:
            # We may need to use ProcessPoolExecutor if this takes too much time.
            # We do not expect too many records. Only ~500 in openerp.
            util._logger.info("Updating more than %s records in account_return_check", ncr.rowcount)

        while data:
            cr.execute(
                """
                UPDATE account_return_check
                   SET message = %s::jsonb->>(id::text)
                 WHERE id IN %s
                """,
                [Json({r[0]: html2plaintext(r[1]) for r in data}), tuple(r[0] for r in data)],
            )
            data = ncr.fetchmany(1000)
