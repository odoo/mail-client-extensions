from odoo.upgrade import util


def migrate(cr, version):
    # comes from l10n_mx_xml_polizas_edi merged in pre-10-modules
    util.remove_view(cr, "l10n_mx_xml_polizas.xml_polizas_edi")
