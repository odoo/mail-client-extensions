# -*- coding: utf-8 -*-
import phonenumbers      # required for migration
from odoo.addons.base.maintenance.migrations import util


def fmt(number, cc):
    try:
        pn = phonenumbers.parse(number, region=cc, keep_raw_input=True)
        if phonenumbers.is_possible_number(pn) and phonenumbers.is_valid_number(pn):
            return phonenumbers.format_number(pn, phonenumbers.PhoneNumberFormat.E164)
    except phonenumbers.phonenumberutil.NumberParseException:
        return number.strip()

def _sanitize(cr, field):
    cr.execute("""
        SELECT p.id, p.{0}, c.code
          FROM res_partner p
          JOIN res_country c ON (c.id = p.country_id)
         WHERE trim(coalesce(p.{0}, '')) != ''
           AND p.sanitized_{0} IS NULL
    """.format(field))
    for pid, number, country_code in util.log_progress(cr.fetchall(), qualifier='res.partner ' + field):
        cr.execute("UPDATE res_partner SET sanitized_{0}=%s WHERE id=%s".format(field),
                   [fmt(number, country_code), pid])
    # ids = (x[0] for x in cr.fetchall())
    # util.recompute_fields(cr, 'res.partner', ids, 'sanitized_' + field)
    cr.execute("""
        UPDATE res_partner
           SET sanitized_{0} = trim({0})
         WHERE sanitized_{0} IS NULL
           AND trim(coalesce({0}, '')) != ''
    """ .format(field))

def migrate(cr, version):
    _sanitize(cr, 'phone')
    _sanitize(cr, 'mobile')


if __name__ == '__main__':
    env = env   # noqa: F821
    migrate(env.cr, None)
    env.cr.commit()
