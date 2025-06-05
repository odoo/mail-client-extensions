from odoo.upgrade import util

documents_18_5_pre_migrate = util.import_script("documents/saas~18.5.1.4/pre-migrate.py")


def migrate(cr, version):
    eb = util.expand_braces

    util.rename_xmlid(
        cr,
        *eb("documents_fleet.ir_actions_server_link_to_vehic{u,}le"),  # fix typo
    )
    documents_18_5_pre_migrate.wrap_documents_server_action(
        cr,
        "documents_fleet.ir_actions_server_link_to_vehicle",
    )
