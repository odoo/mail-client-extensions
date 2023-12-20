# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        r"""
        SELECT id
          FROM ir_ui_view
         WHERE key LIKE 'sale.report\_saleorder\_document%'
           AND key <> 'sale.report_saleorder_document'
        """
    )
    for view_id in cr.fetchall():
        with util.edit_view(cr, view_id=view_id, active=None) as arch:
            for node in arch.xpath(
                '//div[@name="so_total_summary"]/div[@name="total"]/div[1]/table/t[@t-value="json.loads(doc.tax_totals_json)"]'
            ):
                node.attrib["t-value"] = "doc.tax_totals"
