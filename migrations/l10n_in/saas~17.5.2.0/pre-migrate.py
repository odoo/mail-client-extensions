from odoo.upgrade import util


def migrate(cr, version):
    query = """
      UPDATE ir_model_data d
         SET name = concat(c.id, '_p10058')
        FROM res_company c
        JOIN res_country n
          ON n.id = c.account_fiscal_country_id
       WHERE d.model = 'account.account'
         AND d.name = concat(c.id, '_p10054')
         AND n.code = 'IN'
    """
    cr.execute(query)
    if util.module_installed(cr, "l10n_in_edi"):
        util.move_field_to_module(cr, "res.company", "l10n_in_edi_production_env", "l10n_in_edi", "l10n_in")
        util.move_field_to_module(cr, "res.config.settings", "l10n_in_edi_production_env", "l10n_in_edi", "l10n_in")
    util.remove_field(cr, "product.template", "l10n_in_hsn_description")
