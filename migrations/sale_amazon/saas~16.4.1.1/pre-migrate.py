import logging

_logger = logging.getLogger("odoo.upgrade.sale_amazon.16.4.1.1." + __name__)


def migrate(cr, version):
    delete_query = """
        DELETE FROM amazon_offer
        WHERE id NOT IN (
            SELECT MAX(id)
            FROM amazon_offer
            GROUP BY account_id, SKU
        )
    """
    cr.execute(delete_query)

    nb_offers_deleted = cr.rowcount

    if nb_offers_deleted:
        _logger.info(
            "Drop %d duplicate offers (same SKU for the same Amazon account",
            nb_offers_deleted,
        )
