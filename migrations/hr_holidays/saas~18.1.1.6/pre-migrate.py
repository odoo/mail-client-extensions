from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "hr_leave_type", "country_id", "int4")

    cr.execute(
        """
        UPDATE hr_leave_type hlt
           SET country_id = rp.country_id
          FROM res_partner AS rp
          JOIN res_company AS rc
            ON rc.partner_id = rp.id
         WHERE hlt.company_id = rc.id
        """
    )
