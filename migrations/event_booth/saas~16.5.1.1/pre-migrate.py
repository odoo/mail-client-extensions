from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        """
        UPDATE event_booth
        SET contact_phone = contact_mobile
        WHERE contact_phone IS NULL and contact_mobile IS NOT NULL
    """
    )
    util.remove_field(cr, "event.booth", "contact_mobile")
