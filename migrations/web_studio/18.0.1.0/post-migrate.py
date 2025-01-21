import lxml.etree as et

from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        r"""
        SELECT view.id
          FROM ir_ui_view view
          JOIN ir_model_data imd
            ON imd.res_id = view.id
           AND imd.model = 'ir.ui.view'
         WHERE imd.module = 'studio_customization'
           AND view.arch_db->>'en_US' LIKE '%.tax\_totals%'
         """
    )
    for (view,) in cr.fetchall():
        with util.edit_view(cr, view_id=view, active=None) as arch:
            for node in arch.xpath(
                '//t[@t-set="tax_totals" and not(preceding-sibling::t[@t-set="currency"] or following-sibling::t[@t-set="currency"])]'
            ):
                t_value = node.get("t-value")
                prefix, _, rest = t_value.partition(".")
                if rest not in ["tax_totals", "tax_totals or {}"]:
                    continue
                currency_value = f"{prefix}.currency_id"
                newnode = et.Element("t", {"t-set": "currency", "t-value": currency_value})
                node.addnext(newnode)
