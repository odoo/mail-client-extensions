# -*- coding: utf-8 -*-
def migrate(cr, version):
    """In 7.0, the module "account_report_company" was a temporary module and
       its functionnality is now part of the "base" and "account" modules.
    """

    MODULE = 'account_report_company'

    # delete constraints and relations...
    for table in ['constraint', 'relation']:
        cr.execute("""DELETE FROM ir_model_%s
                            WHERE module = (SELECT id
                                              FROM ir_module_module
                                             WHERE name=%%s)
                   """ % table, (MODULE,))

    # remove module
    cr.execute("""
        DELETE FROM ir_module_module
              WHERE name=%s
          RETURNING state
    """, (MODULE,))

    state = cr.fetchone()
    if not state or state[0] not in ('installed', 'to upgrade', 'to remove'):
        return

    # remove views
    cr.execute("""
        SELECT res_id
          FROM ir_model_data
         WHERE module=%s
           AND model=%s
    """, (MODULE, 'ir.ui.view'))

    view_ids = tuple(x[0] for x in cr.fetchall())
    cr.execute('DELETE FROM ir_ui_view WHERE id IN %s', (view_ids,))

    # reassign fields
    cr.execute("""
        UPDATE ir_model_data
           SET module=%s
         WHERE module=%s
           AND name=%s
    """, ('base', MODULE, 'field_res_partner_display_name'))

    cr.execute("""
        UPDATE ir_model_data
           SET module=%s
         WHERE module=%s
           AND name IN %s
    """, ('account', MODULE, ('field_account_invoice_commercial_partner_id', 'field_account_invoice_report_commercial_partner_id')))

    # remove all ir.model.data
    cr.execute("DELETE FROM ir_model_data WHERE module=%s", (MODULE,))
