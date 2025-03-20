from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "card_card", "requires_sync", "boolean", default=False)

    util.create_column(cr, "mailing_mailing", "card_campaign_id", "integer")

    util.create_column(cr, "card_campaign", "content_background", "bytea")
    util.create_column(cr, "card_campaign", "content_button", "varchar")
    util.create_column(cr, "card_campaign", "content_image1_path", "varchar")
    util.create_column(cr, "card_campaign", "content_image2_path", "varchar")

    # Background
    # First move conditionally to campaign then convert to attachment
    # this avoids converting discarded images from other image fields that are removed
    cr.execute("""
        UPDATE card_campaign camp
           SET content_background = el.card_element_image
          FROM card_campaign_element el
         WHERE el.campaign_id = camp.id AND el.card_element_role = 'background'
    """)
    util.convert_binary_field_to_attachment(cr, "card.campaign", "content_background")

    # Button
    cr.execute("""
        UPDATE card_campaign camp
           SET content_button = el.card_element_text
          FROM card_campaign_element el
         WHERE el.campaign_id = camp.id AND el.card_element_role = 'button'
    """)

    # Dynamic Images
    cr.execute("""
        UPDATE card_campaign camp
           SET content_image1_path = el.field_path
          FROM card_campaign_element el
         WHERE el.campaign_id = camp.id AND el.card_element_role = 'image_1'
    """)
    cr.execute("""
        UPDATE card_campaign camp
           SET content_image2_path = el.field_path
          FROM card_campaign_element el
         WHERE el.campaign_id = camp.id AND el.card_element_role = 'image_2'
    """)

    migrate_option_dyn_text_element(cr, "header", "header", with_color=True)
    migrate_option_dyn_text_element(cr, "sub_header", "subheader", with_color=True)
    migrate_option_dyn_text_element(cr, "section", "section_1")
    migrate_option_dyn_text_element(cr, "sub_section1", "subsection_1")
    migrate_option_dyn_text_element(cr, "sub_section2", "subsection_2")

    util.remove_field(cr, "card.campaign", "card_element_ids")
    util.remove_field(cr, "card.campaign", "preview_record_url")
    util.remove_field(cr, "card.card", "record_ref")
    util.remove_model(cr, "card.campaign.element")
    util.remove_model(cr, "card.card.share")

    # set to id 0 of the model to ensure some value in the DB
    # updated to a valid value in end-migrate when possible
    cr.execute(
        """
        UPDATE card_campaign
           SET preview_record_ref = CONCAT(res_model, ',0')
         WHERE preview_record_ref IS NULL
        """
    )


def migrate_option_dyn_text_element(cr, new_field_name, role_name, with_color=False):
    """Migrate elements that can optionally be static or dynamic text"""
    util.create_column(cr, "card_campaign", f"content_{new_field_name}", "varchar")
    util.create_column(cr, "card_campaign", f"content_{new_field_name}_dyn", "bool")
    util.create_column(cr, "card_campaign", f"content_{new_field_name}_path", "varchar")
    if with_color:
        util.create_column(cr, "card_campaign", f"content_{new_field_name}_color", "varchar")

    query = util.format_query(
        cr,
        """
        UPDATE card_campaign camp
           SET {} = TRUE,
               {} = el.field_path
          FROM card_campaign_element el
         WHERE el.campaign_id = camp.id
           AND el.card_element_role = %s
           AND el.value_type = 'field'
        """,
        f"content_{new_field_name}_dyn",
        f"content_{new_field_name}_path",
    )
    cr.execute(query, [role_name])

    query = util.format_query(
        cr,
        """
        UPDATE card_campaign camp
           SET {} = el.card_element_text
          FROM card_campaign_element el
         WHERE el.campaign_id = camp.id
           AND el.card_element_role = %s
           AND el.value_type = 'static'
        """,
        f"content_{new_field_name}",
    )
    cr.execute(query, [role_name])

    if with_color:
        query = util.format_query(
            cr,
            """
            UPDATE card_campaign camp
               SET {} = el.text_color
              FROM card_campaign_element el
             WHERE el.campaign_id = camp.id AND el.card_element_role = %s
            """,
            f"content_{new_field_name}_color",
        )
        cr.execute(query, [role_name])
