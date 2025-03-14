from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "documents.share_single")
    util.remove_view(cr, "documents.share_page")

    util.remove_constraint(cr, "documents_share", "documents_share_owner_id_fkey")
    query = """
        UPDATE documents_share ds
           SET owner_id = rp.id
          FROM res_users ru
          JOIN res_partner rp
            ON rp.id = ru.partner_id
         WHERE ru.id = ds.owner_id
    """
    util.parallel_execute(cr, util.explode_query_range(cr, query, table="documents_share", alias="ds"))
    util.remove_field(cr, "documents.request_wizard", "owner_id")
    util.remove_model(cr, "documents.folder.deletion.wizard")
    util.create_column(cr, "documents_folder", "active", "boolean", default=True)
