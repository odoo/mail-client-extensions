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
           AND (
               view.arch_db->>'en_US' LIKE '%.tax\_totals%'
               OR view.arch_db->>'en_US' LIKE '%account.document\_tax\_totals\_company\_currency\_template%'
           )
        """
    )

    for (view,) in cr.fetchall():
        with util.edit_view(cr, view_id=view, active=None) as arch:
            # Process tax_totals modifications
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

            # Process company currency template modifications
            for node in arch.xpath('//t[@t-call="account.document_tax_totals_company_currency_template"]'):
                parent = node.getparent()
                if parent.get("t-if") == "o.tax_totals.get('display_in_company_currency')":
                    continue
                new_nodes = et.fromstring(
                    """
                  <dummy>
                      <t t-if="o.tax_totals.get('display_in_company_currency')">
                          <t t-set="tax_totals" t-value="o.tax_totals"/>
                          <t t-call="account.document_tax_totals_company_currency_template"/>
                      </t>
                      <t t-else="">
                          <div class="oe_structure"/>
                      </t>
                  </dummy>
                  """
                )
                idx = parent.index(node)
                parent[idx : idx + 1] = new_nodes.getchildren()
