from odoo.upgrade import util


def migrate(cr, version):
    # moving the field l10n_my_edi_industrial_classification from res_company to res_partner
    util.create_column(cr, "res_partner", "l10n_my_edi_industrial_classification", "int4")
    # Up until now, the value on the company is being used and one on the partner ignored.
    # It should be safe to overwrite the partner's value if there is any as it's more likely that
    # the one on the company is the correct value.
    cr.execute("""
        UPDATE res_partner p
           SET l10n_my_edi_industrial_classification = res_company.l10n_my_edi_industrial_classification
          FROM res_company
         WHERE res_company.partner_id = p.id
    """)
    util.remove_column(cr, "res_company", "l10n_my_edi_industrial_classification")
    # Merged during the merge_module but the content has been put in the existing views.
    util.remove_view(cr, "l10n_my_edi.view_partner_form_inherit_l10n_my_myinvois_extended")
    util.remove_view(cr, "l10n_my_edi.view_move_form_inherit_l10n_my_myinvois_extended")
