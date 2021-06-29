# -*- coding: utf-8 -*-


def migrate(cr, version):
    cr.execute(
        """
        INSERT INTO res_lang (name, code, iso_code, translatable, active, direction,
                              date_format, time_format, week_start, grouping, decimal_point, thousands_sep)
             SELECT 'ar_AA_tmp', 'ar_AA_tmp', iso_code, translatable, active, direction,
                    date_format, time_format, week_start, grouping, decimal_point, thousands_sep
               FROM res_lang
              WHERE code = 'ar_AA'
    """
    )
    cr.execute(
        """
        UPDATE res_lang
           SET name = case code
                 when 'ar_AA_tmp' then 'ar_AA'
                 when 'ar_AA' then 'ar_001'
               end,
               code = case code
                  when 'ar_AA_tmp' then 'ar_AA'
                  when 'ar_AA' then 'ar_001'
               end
         WHERE code in ('ar_AA_tmp', 'ar_AA')
    """
    )

    cr.execute("UPDATE ir_translation SET lang='ar_001' WHERE lang = 'ar_AA' ")
    cr.execute("UPDATE res_partner SET lang = 'ar_001' WHERE lang = 'ar_AA' ")
    cr.execute(
        """
        UPDATE ir_default def
           SET json_value = '"ar_001"'
          FROM ir_model_fields field
         WHERE field.id = def.field_id
           AND field.model = 'res.partner'
           AND field.name = 'lang'
           AND def.json_value = '"ar_AA"'
      """
    )

    cr.execute("DELETE FROM res_lang WHERE code = 'ar_AA'")

    cr.execute(
        """
        UPDATE ir_translation
           SET state='to_translate'
         WHERE state NOT IN ('translated', 'to_translate', 'inprogress')
         """
    )
