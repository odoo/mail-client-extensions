from odoo.upgrade import util


def check_and_replace_mobile(cr, model, parts):
    """
    If path ends with mobile, replace with phone and validate the new path.
    Returns the new path if valid, otherwise returns None.
    """
    if parts[-1] in ("mobile", "partner_mobile"):
        parts[-1] = parts[-1].replace("mobile", "phone")
        resolved_parts = util.resolve_model_fields_path(cr, model, parts)
        if len(resolved_parts) == len(parts):
            return ".".join(parts)
    return None


def migrate(cr, version):
    cr.execute("""
        SELECT id,
               model,
               STRING_TO_ARRAY(phone_field, '.') AS parts
          FROM whatsapp_template
         WHERE phone_field LIKE '%mobile'
    """)

    for template in cr.dictfetchall():
        updated_phone_field = check_and_replace_mobile(cr, template["model"], template["parts"])
        if updated_phone_field:
            cr.execute(
                "UPDATE whatsapp_template SET phone_field = %s WHERE id = %s",
                (updated_phone_field, template["id"]),
            )

    cr.execute("""
        SELECT var.id,
               STRING_TO_ARRAY(var.field_name, '.') AS parts,
               tmpl.model
          FROM whatsapp_template_variable var
          JOIN whatsapp_template tmpl
            ON var.wa_template_id = tmpl.id
         WHERE var.field_type = 'field'
           AND var.field_name LIKE '%mobile'
    """)

    for variable in cr.dictfetchall():
        updated_field_name = check_and_replace_mobile(cr, variable["model"], variable["parts"])
        if updated_field_name:
            cr.execute(
                "UPDATE whatsapp_template_variable SET field_name = %s WHERE id = %s",
                (updated_field_name, variable["id"]),
            )

    util.change_field_selection_values(cr, "whatsapp.template.variable", "field_type", {"user_mobile": "user_phone"})
