# -*- coding: utf-8 -*-

def migrate(cr, version):
    cr.execute("""
        UPDATE crm_team
        SET dashboard_graph_model = CASE dashboard_graph_model
            WHEN 'sales' THEN 'sale.report'
            WHEN 'invoices' THEN 'account.invoice.report'
            ELSE dashboard_graph_model
        END
    """)
