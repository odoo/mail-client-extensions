# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # some rows from account_analytic_account needs to be copied to the new model, depending on their type
    cr.execute("""
        CREATE TABLE IF NOT EXISTS sale_subscription(
            id SERIAL NOT NULL PRIMARY KEY,
            analytic_account_id integer NOT NULL,
            user_id integer,
            manager_id integer,
            date_start date,
            date date,
            state varchar,
            pricelist_id integer,
            type varchar,
            description text,
            recurring_rule_type varchar,
            recurring_interval integer,
            recurring_next_date date,
            template_id integer,
            create_date timestamp without time zone,
            write_date timestamp without time zone,
            create_uid integer,
            write_uid integer
            )
        """)
    cr.execute("""
        INSERT INTO sale_subscription (user_id,manager_id,state,analytic_account_id,date_start,date,pricelist_id,type,description,recurring_rule_type,recurring_interval,recurring_next_date,create_date,write_date,create_uid,write_uid,template_id)
             (SELECT user_id,manager_id,state,id as analytic_account_id,date_start,date,pricelist_id,type,description,recurring_rule_type,recurring_interval,recurring_next_date,create_date,write_date,create_uid,write_uid,template_id
                        FROM account_analytic_account
                        WHERE (type = 'contract' AND recurring_invoices = 't') OR type = 'template')
        """)

    cr.execute("UPDATE sale_subscription SET state='cancel' WHERE state='cancelled'")

    # keep relation between contracts and templates since all ids have changed when switching tables
    cr.execute("""
        UPDATE sale_subscription
            SET template_id = query.ss_id
            FROM (
                SELECT ss.id AS ss_id, aaa.id AS aa_id
                FROM sale_subscription AS ss, account_analytic_account AS aaa
                WHERE ss.analytic_account_id = aaa.id AND
                      aaa.type = 'template') AS query
            WHERE sale_subscription.template_id IS NOT NULL AND
                  sale_subscription.template_id = query.aa_id
        """)

    # cleanup lines
    cr.execute("""
        DELETE FROM account_analytic_invoice_line
              WHERE analytic_account_id NOT IN (SELECT analytic_account_id FROM sale_subscription)
    """)
    cr.execute("ALTER TABLE account_analytic_invoice_line DROP CONSTRAINT account_analytic_invoice_line_analytic_account_id_fkey")

    util.rename_model(cr, 'account.analytic.invoice.line', 'sale.subscription.line')
    util.create_column(cr, 'sale_subscription_line', 'sold_quantity', 'double precision')
    cr.execute("""
        UPDATE sale_subscription_line AS ssl SET
            sold_quantity = "quantity",
            analytic_account_id = query.id
            FROM (SELECT id,analytic_account_id
                    FROM sale_subscription) as query
            WHERE query.analytic_account_id = ssl.analytic_account_id
        """)
    # move chatter messages from analytic account to subscription
    cr.execute("""
        UPDATE mail_message SET
            model='sale.subscription',
            res_id=query.id
            FROM (SELECT id,analytic_account_id FROM sale_subscription) as query
            WHERE res_id=query.analytic_account_id AND
                  model='account.analytic.account'
        """)

    # if this key is set, we'll not create sale orders from contracts
    # this will prevent some databases from creating completely purposeless SOs
    cr.execute("SELECT value FROM ir_config_parameter WHERE key=%s", ('migration.sale_contract.no-create-sale-orders',))
    create_orders = cr.fetchone() or False

    if not create_orders:
        # standard and prepaid contracts become sales orders (EVERYTHING is a sales order as from v9)
        env = util.env(cr)
        cr.execute("""
            SELECT id, name, partner_id, manager_id, company_id, pricelist_id,
                   coalesce(date_start, create_date, now() at time zone 'utc') as date_start,
                   code
                FROM account_analytic_account
                WHERE type = 'contract' AND
                      state in ('pending', 'open')
                 AND partner_id is not null
                 AND pricelist_id is not null
            """)
        aa_ids = cr.dictfetchall()
        # lines that come from supplier invoices or timesheets needs to be in the new sales order
        cr.execute("""
            SELECT aal.product_id,aal.name,aal.product_uom_id AS product_uom,0 AS product_uom_qty,aal.unit_amount AS qty_delivered,account_id,aal.company_id
                FROM account_analytic_line AS aal, account_analytic_account AS aaa, account_analytic_journal AS aaj, hr_timesheet_invoice_factor AS fct
                WHERE aaa.type = 'contract' AND
                      aaa.state in ('pending', 'open') AND
                      aal.journal_id = aaj.id AND
                      aal.account_id = aaa.id AND
                      (
                        aaj.type = 'purchase'
                        OR
                        (aaj.type = 'general' AND
                         aal.to_invoice = fct.id AND
                         fct.factor < 100)
                      )
            """)
        sol_vals = cr.dictfetchall()
        so_ids = []
        # no problem using the orm, sale was migrated decades ago in computer time
        default_uom_id = env['ir.model.data'].xmlid_to_res_id('product.product_uom_unit')

        # product_id was not mandatory in saas-6, see product migration
        Product = env['product.product'].with_context(active_test=False)
        default_product_id = Product.search([('default_code', '=', 'GEN_ODOO9_MIG')], limit=1).id

        SaleOrder = env['sale.order'].with_context(mail_notrack=True)

        for aa in aa_ids:
            if not (aa.get('partner_id') and aa.get('pricelist_id')):
                # no customer or pricelist, you probably don't want a SO in that case
                continue
            order_lines = [(0, False, dict(sol)) for sol in filter(lambda val: aa['id'] == val['account_id'], sol_vals)]
            if order_lines:  
                # checking mandatory fields in sol
                for line in order_lines:
                    line[2].pop('account_id')  # avoid warning for non-existing field
                    line[2]['product_id'] = line[2]['product_id'] or default_product_id
                    line[2]['product_uom'] = line[2]['product_uom'] or default_uom_id
                so = SaleOrder.create({
                    'partner_id': aa['partner_id'],
                    'user_id': aa['manager_id'],
                    'state': 'sale',
                    'project_id': aa['id'],
                    'company_id': aa['company_id'],
                    'pricelist_id': aa['pricelist_id'],
                    'date_order': aa['date_start'],
                    'order_line': order_lines,
                })
                so_ids.append((so.id, aa['id'], aa['code'], aa['name']))
        if so_ids:
            values_str = ','.join(["('sale.order',%s,1,%s,'comment',LOCALTIMESTAMP,LOCALTIMESTAMP)"] * len(so_ids))
            values_args = sum((
                              (so_id, 'Order created during the migration to Odoo 9.0 from Contract %s - %s (#%s)' %
                                  (aa_code, aa_name, aa_id))
                              for (so_id, aa_id, aa_code, aa_name) in so_ids
                              ), ())
            cr.execute("""
                INSERT INTO mail_message(
                    model, res_id, author_id, body, message_type, create_date, date
                )
                VALUES """ + values_str,
                values_args)

    # we prevented deletion in analytic for this module, set it free now
    util.delete_model(cr, 'account.analytic.journal')
    util.delete_model(cr, 'hr_timesheet_invoice.factor')
