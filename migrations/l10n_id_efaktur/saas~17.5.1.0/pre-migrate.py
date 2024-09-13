from odoo.upgrade import util


def migrate(cr, version):
    # res.partner: remove l10n_id_tax_address and l10n_id_tax_name, append the 2 existing fields to `comment`
    # if exists.
    util.explode_execute(
        cr,
        """
        UPDATE res_partner
           SET comment = format('%s\nTax name: %s\nTax address: %s', comment, l10n_id_tax_name, l10n_id_tax_address)
         WHERE l10n_id_tax_name IS NOT NULL
            OR l10n_id_tax_address IS NOT NULL
        """,
        table="res_partner",
    )

    util.remove_field(cr, "res.partner", "l10n_id_tax_name")
    util.remove_field(cr, "res.partner", "l10n_id_tax_address")

    util.add_to_migration_reports(
        message="""
        <details>
            <summary>
                <p>The Tax Name and Tax Address fields on the Contacts and in the Settings are now deprecated.</p>
                <p>Check on customers' internal notes to get the previous data for Tax Name and Tax Address.</p
                <p>Please create a new invoice address and set the standard name and address field if necessary.</p>
            </summary>
        </details>
        """,
        format="html",
    )

    util.remove_field(cr, "account.move", "l10n_id_csv_created")

    util.remove_field(cr, "res.config.settings", "l10n_id_tax_name")
    util.remove_field(cr, "res.config.settings", "l10n_id_tax_address")

    # l10n_id_attachment_id is used in post to move attachments to l10n_id_efaktur_document
    util.remove_field(cr, "account.move", "l10n_id_attachment_id", drop_column=False)

    util.remove_menus(cr, [util.ref(cr, "l10n_id_efaktur.menu_efaktur_action")])
