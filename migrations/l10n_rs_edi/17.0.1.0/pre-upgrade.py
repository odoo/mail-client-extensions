from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "account_move", "l10n_rs_edi_uuid", "varchar")
    util.create_column(cr, "account_move", "l10n_rs_edi_is_eligible", "boolean")
    util.create_column(cr, "account_move", "l10n_rs_tax_date_obligations_code", "varchar")

    query = """
        UPDATE account_move m
           SET l10n_rs_tax_date_obligations_code = '3'
          FROM res_company c
          JOIN res_country f
            ON f.id = c.account_fiscal_country_id
         WHERE c.id = m.company_id
           AND f.code = 'RS'
    """
    util.explode_execute(cr, query, table="account_move", alias="m")

    func = None
    if cr._cnx.server_version < 130000:
        cr.execute("SELECT 1 FROM pg_proc WHERE proname = 'gen_random_uuid'")
        if not cr.rowcount:
            func = """
                CREATE FUNCTION gen_random_uuid()
                RETURNS uuid as $body$
                    SELECT string_agg(
                               CASE i
                                   WHEN 13 THEN '4' -- uuid4 spec
                                   WHEN 17 THEN to_hex(8 + width_bucket(random(), 0, 1, 4) - 1)  -- uuid4 spec, random from 8,9,10,11
                                   ELSE to_hex(width_bucket(random(), 0, 1, 16) - 1) -- random hex value
                               END,
                               ''
                           )::uuid
                      FROM generate_series(1, 32) as data(i);
                $body$
                LANGUAGE 'sql'
                VOLATILE
                PARALLEL SAFE
            """
            cr.execute(func)

    query = """
        UPDATE account_move m
           SET l10n_rs_edi_is_eligible = true,
               l10n_rs_edi_uuid = gen_random_uuid()
          FROM res_company c
          JOIN res_country f
            ON f.id = c.account_fiscal_country_id
         WHERE c.id = m.company_id
           AND f.code = 'RS'
           AND m.move_type IN ('out_invoice', 'out_refund')
    """
    util.explode_execute(cr, query, table="account_move", alias="m")

    if func:
        cr.execute("DROP FUNCTION gen_random_uuid")
