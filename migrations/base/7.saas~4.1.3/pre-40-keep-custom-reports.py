# -*- coding: utf-8 -*-
import uuid

def migrate(cr, version):
    reports_modules = tuple("""
        account
        hr_attendance
        hr_expense
        hr_payroll
        hr_timesheet_invoice
        lunch
        mrp
        purchase
        sale
    """.split())

    cr.execute("""SELECT r.id, array_agg(x.id) xids
                    FROM ir_act_report_xml r
                    JOIN ir_model_data x
                      ON (x.model = 'ir.actions.report.xml' AND x.res_id = r.id)
                   WHERE (report_rml_content_data IS NOT NULL
                      OR  report_sxw_content_data IS NOT NULL)
                     AND x.module IN %s
                GROUP BY r.id
                """, (reports_modules,))
    for rid, xids in cr.fetchall():
        u = str(uuid.uuid4()).split('-')[0]
        cr.execute("""UPDATE ir_act_report_xml
                         SET report_name = report_name || '.' || %s,
                             name = name || ' (edited)'
                       WHERE id = %s
                   """, (u, rid))
        cr.execute("DELETE FROM ir_model_data WHERE id IN %s", (tuple(xids),))
