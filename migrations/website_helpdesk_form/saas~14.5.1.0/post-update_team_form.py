from odoo.upgrade import util


def migrate(cr, version):
    # update custom team form view according to 'Submit a Ticket'(website_helpdesk_form.ticket_submit_form)
    # as it has created using that view
    cr.execute(
        r"""
        UPDATE ir_ui_view
           SET arch_db = (SELECT arch_db FROM ir_ui_view WHERE id = %s)
         WHERE id IN (SELECT res_id
                        FROM ir_model_data
                       WHERE name ~ '^team_form_\d+$'
                         AND model = 'ir.ui.view'
                         AND module = 'website_helpdesk_form'
                     )
        """,
        [util.ref(cr, "website_helpdesk_form.ticket_submit_form")],
    )
