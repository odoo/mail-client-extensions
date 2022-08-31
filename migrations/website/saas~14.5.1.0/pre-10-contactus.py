# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    # If one of the views related to /contactus has been COWed, backup them all
    # to leave an untouched copy of the contact us pages.
    view_keys = [
        "website.contactus",
        "website.contactus_form",  # was 'website_form.xx' before module_merge
        "website_crm.contactus_form",
        "website.contactus_thanks",  # was 'website_form.xx' before module_merge
    ]
    t_called_view_keys = [
        "website.company_description",
        "website.company_description_google_map",
    ]
    oe_structure_view_keys = [
        # both were 'website_form.xx' before module_merge
        "website.contactus_thanks_oe_structure_website_form_contact_us_thanks_1",
        "website.contactus_thanks_oe_structure_website_form_contact_us_thanks_2",
    ]

    has_modified_views = has_cow_view(cr, view_keys + oe_structure_view_keys + t_called_view_keys)
    # if `website_crm` was installed, keep a backup of the form (which create
    # leads), as the new one won't send lead by default
    crm_installed = util.module_installed(cr, "website_crm")

    if has_modified_views or crm_installed:
        # Remove view's xml_id so they are not removed/updated by the upgrade
        for key in view_keys + t_called_view_keys:
            remove_xml_id(cr, key)
        # Same for pages
        remove_xml_id(cr, "website.contactus_page")
        remove_xml_id(cr, "website.contactus_page_ir_ui_view")
        remove_xml_id(cr, "website.contactus_thanks")
        remove_xml_id(cr, "website.contactus_thanks_ir_ui_view")
        # Keep customized contact pages as old unpublished pages
        backup_data = backup_contactus_related_views(cr, view_keys + oe_structure_view_keys)
        backup_data.extend(backup_contactus_related_views(cr, t_called_view_keys, True))
        if backup_data:
            li = "".join(
                "<li>{}</li>".format(util.get_anchor_link_to_record("ir.ui.view", vid, vname))
                for vid, vname in backup_data
            )
            util.add_to_migration_reports(
                f"""
                    <details>
                    <summary>
                       The contactus page has been improved so now it is fully customizable and static, which is  also faster.
                       But your original contactus page is also available, so you should either:<br/>
                        - Keep the new one and delete the back up one (Use 'Contact Us' page)<br/>
                        - If you want to use old 'Contact Us' page (Use 'Contact Us (v15 upgrade backup)' page):
                    </summary>
                    <ul>{li}</ul>
                    </details>
                """,
                "Website",
                format="html",
            )
    else:
        util.remove_view(cr, "website.company_description")
        util.remove_view(cr, "website.company_description_google_map")
        # was 'website_form.contactus_form' before module_merge, and
        # `website.contactus_form` doesn't exists anymore
        util.remove_view(cr, "website.contactus_form")
        # as `website.company_description` is previously removed, we need to ensure that the `website.contactus` view
        # will be updated to the new saas~14.5 one (needed for website/saas~14.5.1.0/post-define-contactus-details.py)
        util.force_noupdate(cr, "website.contactus", noupdate=False)


def has_cow_view(cr, xml_ids):
    cr.execute(
        """
        SELECT COUNT(*)
          FROM ir_ui_view
         WHERE website_id IS NOT NULL
           AND key IN %s
    """,
        [tuple(xml_ids)],
    )
    return cr.fetchone()[0] > 0


def backup_contactus_related_views(cr, keys, keep_key=False):
    """Backup COW views + their page (if exists)."""
    cr.execute(
        """
        UPDATE website_page p
           SET is_published = false,
               website_indexed = false,
               url = concat('/pre-v15-upgrade-', right(url, -1))
          FROM ir_ui_view v
         WHERE p.view_id = v.id
           AND v.key IN %s
           AND v.website_id IS NOT NULL
    """,
        [tuple(keys)],
    )
    cr.execute(
        """
        UPDATE ir_ui_view
           SET {key}
               name = name || ' (v15 upgrade backup)'
         WHERE key IN %s
           AND website_id IS NOT NULL
        RETURNING id, name
    """.format(
            key="" if keep_key else "key = key || '_v15_upgrade_backup',"
        ),
        [tuple(keys)],
    )
    return cr.fetchall()


def remove_xml_id(cr, xml_id):
    module, _, name = xml_id.partition(".")
    cr.execute(
        """
        DELETE
          FROM ir_model_data
         WHERE module = %s
           AND name = %s
    """,
        [module, name],
    )
