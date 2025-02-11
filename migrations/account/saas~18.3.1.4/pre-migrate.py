from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "account_journal", "incoming_einvoice_notification_email", "varchar")
    cr.execute(
        """
        UPDATE account_journal AS j
           SET incoming_einvoice_notification_email = c.email
          FROM res_company AS c
         WHERE c.id = j.company_id;
        """
    )
