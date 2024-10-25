from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        """
        SELECT 1
          FROM ir_model_fields
         WHERE model = 'hr.contract.type'
           AND name = 'name'
           AND translate IS NOT TRUE
        """
    )
    if cr.rowcount:
        # commonly installed custom modules switch this field to non-translatable,
        # we ensure here that the field is as per the standard Odoo code
        util.convert_field_to_translatable(cr, "hr.contract.type", "name")
