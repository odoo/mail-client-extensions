# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def _db_openerp(cr, version):
    util.merge_module(cr, 'sale_contract', 'account_analytic_analysis')
    cr.execute("DELETE FROM ir_model_data WHERE module='base' and name='module_sale_contract'")
    cr.execute("UPDATE account_analytic_account SET recurring_invoices='t' WHERE contract_type='subscription'")

    cr.execute("""
        DELETE FROM openerp_enterprise_database_app
              WHERE module_id IN (SELECT id
                                    FROM ir_module_module
                                   WHERE name IN ('contacts', 'hr_applicant_document', 'im_chat')
                                 )
    """)

    """
        Journal id=12: "Note de crédits sur ventes" is used from two different sale journal
        (id=1 "Journal des Ventes" and id=96 "Journal de ventes SAAS"). Thus we need to 
        associate the refund to one of these two journal, in our case it was a human mistake,
        we should have created two different refund journal at the time but we didn't. So we
        will associate the refund to journal id=1 and create another refund sequence for journal id=96
    """

    util.create_column(cr, 'account_journal', 'refund_sequence_id', 'integer')
    util.create_column(cr, 'account_journal', 'refund_sequence', 'bool')
    cr.execute("""UPDATE account_journal
                    SET refund_sequence_id = 35,
                    refund_sequence = true
                    WHERE id = 1
                """)

    #Create new refund sequence for journal id=96
    cr.execute("""INSERT INTO ir_sequence(name, implementation, prefix, padding, number_increment, number_next, use_date_range, company_id)
                     VALUES ('Journal de ventes SAAS', 'no_gap', 'RSAAS/%(year)s/', 4, 1, 1, true, 1)
                     RETURNING id""")
    seq_id = cr.fetchone()
    cr.execute("""UPDATE account_journal SET 
                    refund_sequence = true,
                    refund_sequence_id = %s
                    WHERE id = 96""", 
                    (seq_id,))
    
    # we have some invoices with incorrect type so we must correct them first
    cr.execute("""UPDATE account_invoice set type='out_refund' WHERE type = 'out_invoice' AND journal_id in (12, 15, 16)""")

    # Update journal reference
    TABLES = ['account_move_line', 'account_move', 'account_invoice']
    for table in TABLES:
        cr.execute("""UPDATE %s
                        SET journal_id = 1
                        WHERE journal_id = 12
                        """ % (table,))

    # Delete journalid=12
    cr.execute("""DELETE FROM account_journal WHERE id=12""")
    
    # change journal id=97 (Notes de crédit sur ventes (Rect.)) that is only used for correction, rename it correction
    # and create a new sequence for it.
    cr.execute("""INSERT INTO ir_sequence(name, implementation, prefix, padding, number_increment, number_next, use_date_range, company_id)
                     VALUES ('Corrections', 'no_gap', 'CORR/%(year)s/', 4, 1, 1, true, 1)
                     RETURNING id""")
    seq_id = cr.fetchone()
    cr.execute("""UPDATE account_journal SET
                    name = 'Corrections',
                    type = 'sale',
                    sequence_id = %s,
                    refund_sequence = true,
                    refund_sequence_id = 175
                    WHERE id = 97""", 
                    (seq_id,))

    # theses records have already been deleted in prod database, but local copies may still have them
    cr.execute("DELETE FROM account_tax WHERE id IN (1377, 1379, 1380, 1381)")
    cr.execute("ALTER TABLE account_analytic_line ALTER COLUMN general_account_id DROP NOT NULL")
    cr.execute("UPDATE account_analytic_line SET general_account_id=NULL WHERE id=1525")

    # remove old inherited views
    for view in [2274, 2318, 7336, 7361, 7437, 7443, 7743, 8225, 8226]:
        util.remove_view(cr, view_id=view, silent=True)
    util.remove_view(cr, 'openerp_payment.view_partners_form_payment_defaultcreditcard')
    util.remove_view(cr, 'openerp_enterprise.view_partners_form_plan')
    util.force_noupdate(cr, 'openerp_enterprise.view_customer_invoice_lines_popup', False)

    with util.edit_view(cr, view_id=8183) as arch:
        bad = arch.find('.//xpath')
        bad.getparent().remove(bad)

    cr.execute("DELETE FROM ir_filters WHERE id=11151")
    cr.execute("DELETE FROM ir_rule WHERE id=260")
    # FORGOT HISTORY
    cr.execute("TRUNCATE im_chat_message")

    # fix some custom server actions
    cr.execute("UPDATE ir_act_server SET code=replace(code, 'message.type', 'message.message_type') WHERE id in (2265, 2378)")
    cr.execute("UPDATE ir_act_server SET code=replace(code, 'type', 'message_type') WHERE id=2278")


def _andrew(cr, version):
    # remove views inheriting deprecated view:
    views = (
        'stock.move.form.nel',
        'transfer.nel',
    )
    cr.execute("select id from ir_ui_view where name in %s", [views])

    for view_id, in cr.fetchall():
        util.remove_view(cr, view_id=view_id)

    # disable problematic views
    views = (
        'hr.nel',
        'statement.line.nel',
        'Asset.nel',
        'product.template.search.nel',
        'purchase.order.inherit_288',
    )
    cr.execute("UPDATE ir_ui_view SET active=false WHERE name IN %s", [views])

def migrate(cr, version):
    cr.execute("SELECT value FROM ir_config_parameter WHERE key=%s", ('database.uuid',))
    [uuid] = cr.fetchone()
    {
        '05a64ced-5b98-488d-a833-a994f9b1dd80': _db_openerp,    # test
        '8851207e-1ff9-11e0-a147-001cc0f2115e': _db_openerp,    # prod
        '0950c4ec-5bda-11e5-816e-002590a742c0': _andrew,        # andrew-alliance-sept
        '1231bd5a-4d59-11e3-80e6-f23c91dbe612': _andrew,        # andrew-alliance
    }.get(uuid, lambda *a: None)(cr, version)
