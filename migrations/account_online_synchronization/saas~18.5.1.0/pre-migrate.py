from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "account.online.link", "provider_data")

    util.create_column(cr, "account_online_link", "renewal_contact_email", "varchar")
    cr.execute("""
        UPDATE account_online_link AS link
           SET renewal_contact_email = journal.renewal_contact_email
          FROM account_journal AS journal
         WHERE journal.account_online_link_id = link.id
           AND journal.renewal_contact_email IS NOT NULL
    """)
    util.remove_column(cr, "account_journal", "renewal_contact_email")
