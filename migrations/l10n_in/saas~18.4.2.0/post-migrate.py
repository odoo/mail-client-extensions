from odoo.upgrade import util


def migrate(cr, version):
    # remove unused taxes of TCS section 206C(1H)
    query = """
        SELECT CONCAT(d.module, '.', d.name)
          FROM ir_model_data d
    CROSS JOIN res_company c
         WHERE d.model = 'account.tax'
           AND d.module = 'account'
           AND d.name IN (c.id || '_tcs_0_1_us_206c_1h_sog', c.id || '_tcs_1_us_206c_1h_sog')
     """
    cr.execute(query)
    if cr.rowcount:
        util.delete_unused(cr, *[x for (x,) in cr.fetchall()])

    # deactivate used taxes of TCS section 206C(1H)
    cr.execute(
        """
        UPDATE account_tax t
           SET active = FALSE
          FROM ir_model_data md
         WHERE md.model = 'l10n_in.section.alert'
           AND t.l10n_in_section_id = md.res_id
           AND md.name = 'tcs_section206c1h_g'
           AND md.module = 'l10n_in'
        """
    )
