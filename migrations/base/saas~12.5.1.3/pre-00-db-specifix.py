from odoo.addons.base.maintenance.migrations import util


def _openerp(cr, version):
    # remove some duplicated invoice lines
    cr.execute(
        """
        DELETE FROM account_invoice_line
              WHERE id IN (2545, 2546, 2547, 2548, 3453, 1863111)
    """
    )
    # remove 2 canceled test invoices
    util.remove_record(cr, ("account.invoice", 12320))
    util.remove_record(cr, ("account.invoice", 12321))

    util.remove_view(cr, view_id=11951)
    util.remove_record(cr, ("ir.attachment", 12766056))  # bad compiled scss
    # see OPW-2154508, an inherit view was added to change a text that has already been changed in 13.0.
    util.remove_view(cr, view_id=12522)

    # use defined view in server actions
    cr.execute(r"""
        UPDATE ir_act_server
           SET code = regexp_replace(code, '\ycrm_case_form_view_oppor\y', 'crm_lead_view_form', 'g')
         WHERE code ~ '\ycrm_case_form_view_oppor\y'
    """)

def migrate(cr, version):
    util.dispatch_by_dbuuid(cr, version, {"8851207e-1ff9-11e0-a147-001cc0f2115e": _openerp})
