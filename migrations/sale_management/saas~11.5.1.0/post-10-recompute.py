# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # Create section lines
    # Then re-generate the sequence to ensure proper order
    if util.module_installed(cr, "sale_quotation_builder"):
        cr.execute(
            """
            INSERT INTO sale_order_template_line
                (sale_order_template_id, layout_category_id, sequence, display_type, name, price_unit, product_uom_qty)
                SELECT s.sale_order_template_id, s.layout_category_id, min(s.sequence)-5, 'line_section', l.name, 0, 0
                FROM sale_order_template_line s INNER JOIN sale_layout_category l on s.layout_category_id=l.id
                GROUP BY s.sale_order_template_id, s.layout_category_id, l.name
                ORDER BY s.sale_order_template_id, s.layout_category_id
        """
        )
        cr.execute(
            """
            WITH new_sequence AS (
                SELECT s.id,row_number() OVER (PARTITION BY s.sale_order_template_id) as sequence
                FROM sale_order_template_line s INNER JOIN sale_layout_category l on s.layout_category_id=l.id
                ORDER BY s.sale_order_template_id, l.sequence, l.id, COALESCE(s.sequence, 0), id
            )
            UPDATE sale_order_template_line
            SET sequence=new_sequence.sequence
            FROM new_sequence
            WHERE sale_order_template_line.id=new_sequence.id
        """
        )
