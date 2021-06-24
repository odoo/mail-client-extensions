# -*- coding: utf-8 -*-

import odoo.upgrade.util.snippets as snip
from odoo.upgrade import util


def migrate(cr, version):
    migrate_contactus(cr)

    if util.table_exists(cr, "website_configurator_feature"):
        util.create_column(cr, "website_configurator_feature", "feature_url", "varchar")
        util.create_column(cr, "website_configurator_feature", "menu_company", "boolean")
        util.create_column(cr, "website_configurator_feature", "menu_sequence", "int4")
        util.remove_field(cr, "website.configurator.feature", "type")
        util.rename_field(
            cr, "website.configurator.feature", "website_types_preselection", "website_config_preselection"
        )

    # website_animate was merged into website but none of its views remains
    util.remove_view(cr, "website.o_animate_options")
    util.remove_view(cr, "website.no-js_fallback")

    # header template migration
    util.remove_view(cr, "website.template_header_default_oe_structure_header_default_1")
    util.remove_view(cr, "website.template_header_hamburger_oe_structure_header_hamburger_1")
    util.remove_view(cr, "website.template_header_slogan_oe_structure_header_slogan_2")
    util.remove_view(cr, "website.template_header_boxed_oe_structure_header_boxed_2")
    util.remove_view(cr, "website.template_header_image_oe_structure_header_image_2")

    # minimalist header to remove -> re-enable the default one on the right
    # websites (which should already have a cow'ed view for it but disabled)
    cr.execute("SELECT website_id FROM ir_ui_view WHERE key = 'website.template_header_minimalist' and active = TRUE")
    website_ids = [website_id for (website_id,) in cr.fetchall()]
    if website_ids:
        cr.execute(
            "UPDATE ir_ui_view SET active = TRUE WHERE key = 'website.template_header_default' and website_id IN %s",
            [tuple(website_ids)],
        )
    util.remove_view(cr, "website.template_header_minimalist")


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


def migrate_submit_url(cr):
    """Reflect /website_form/ URL change inside pages and HTML fields."""
    cr.execute(
        """
        UPDATE ir_ui_view
           SET arch_db = REPLACE(arch_db, 'action="/website_form/"', 'action="/website/form/"')
         WHERE type = 'qweb'
           AND arch_db LIKE '%/website\\_form/%'
    """
    )
    for table, column in snip.get_html_fields(cr):
        cr.execute(
            f"""
            UPDATE {table}
               SET {column} = REPLACE({column}, 'action="/website_form/"', 'action="/website/form/"')
             WHERE {column} LIKE '%/website\\_form/%'
        """
        )


def backup_contactus_related_views(cr, keys, keep_key=False):
    """Backup COW views + their page (if exists)."""
    cr.execute(
        """
        UPDATE website_page p
           SET is_published = false,
               website_indexed = false,
               url = concat('/migration-old-', right(url, -1))
          FROM ir_ui_view v
         WHERE p.view_id = v.id
           AND v.key IN %s
    """,
        [tuple(keys)],
    )
    cr.execute(
        """
        UPDATE ir_ui_view
           SET {key}
               name = name || ' (migration old)'
         WHERE key IN %s
    """.format(
            key="" if keep_key else "key = key || '_migration_old',"
        ),
        [tuple(keys)],
    )


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


def migrate_contactus(cr):
    migrate_submit_url(cr)

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
        remove_xml_id(cr, "website.contactus_thanks")
        # Keep customized contact pages as old unpublished pages
        backup_contactus_related_views(cr, view_keys + oe_structure_view_keys)
        backup_contactus_related_views(cr, t_called_view_keys, True)
    else:
        util.remove_view(cr, "website.company_description")
        util.remove_view(cr, "website.company_description_google_map")
        # was 'website_form.contactus_form' before module_merge, and
        # `website.contactus_form` doesn't exists anymore
        util.remove_view(cr, "website.contactus_form")

    util.remove_view(cr, "website.remove_external_snippets")
