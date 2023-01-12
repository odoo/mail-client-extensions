# -*- coding: utf-8 -*-
import logging
import math

from multiprocessing import Process, Semaphore

from odoo.addons.base.maintenance.migrations import util
from odoo.addons.phone_validation.tools import phone_validation
from odoo.exceptions import UserError


_logger = logging.getLogger("odoo.addons.base.maintenance.migrations.crm.saas-12.4." + __name__)


def validate_phone(cr, lead_ids, out_sem):
    correct_ids = []
    incorrect_ids = []
    for lead_id, phone, country_code in lead_ids:
        try:
            if phone_validation.phone_parse(phone, country_code or None):  # otherwise library not installed
                correct_ids.append(lead_id)
                if len(correct_ids) > 1000:
                    out_sem.acquire()
                    cr.execute("UPDATE crm_lead SET phone_state='correct' WHERE id in %s", [tuple(correct_ids)])
                    out_sem.release()
                    correct_ids = []
        except UserError:
            incorrect_ids.append(lead_id)

    if correct_ids:
        out_sem.acquire()
        cr.execute("UPDATE crm_lead SET phone_state='correct' WHERE id in %s", [tuple(correct_ids)])
        out_sem.release()
    if incorrect_ids:
        out_sem.acquire()
        cr.execute("UPDATE crm_lead SET phone_state='incorrect' WHERE id in %s", [tuple(incorrect_ids)])
        out_sem.release()


def migrate(cr, version):
    _logger.info("Starting phone_valid computation")
    query = "UPDATE crm_lead SET phone_state = 'empty' WHERE phone_state IS NULL AND (phone IS NULL OR phone='')"
    util.parallel_execute(cr, util.explode_query_range(cr, query, table="crm_lead"))

    query = """
        SELECT l.id, l.phone, c.code
          FROM crm_lead l
     LEFT JOIN res_country c ON c.id=l.country_id
         WHERE phone_state IS NULL
    """
    util.parallel_execute(cr, util.explode_query_range(cr, query, table="crm_lead", alias="l"))

    lead_ids = [(res[0], res[1], res[2]) for res in cr.fetchall()]
    _logger.info("Computing phone_valid")
    nbr_thd = min(util.cpu_count(), 8)
    chunksize = int(math.ceil(len(lead_ids) / float(nbr_thd)))
    lead_chunks = (
        [lead_ids[i : i + chunksize] for i in range(0, len(lead_ids), chunksize)]  # noqa: E203
        if chunksize > 0
        else [lead_ids]
    )
    lst_thd = []
    out_sem = Semaphore()
    for chunk in lead_chunks:
        p = Process(target=validate_phone, args=(cr, chunk, out_sem))
        lst_thd.append(p)
        p.start()

    for p in lst_thd:
        p.join()

    _logger.info("Computing email_state")
    query = """
        UPDATE crm_lead
           SET email_state = CASE WHEN email_from IS NULL or email_from = ''
                                  THEN 'empty'
                                  WHEN email_from SIMILAR TO '([^ ,;<@]+@[^> ,;]+)'
                                  THEN 'correct'
                                  ELSE 'incorrect'
                              END
         WHERE email_state IS NULL
    """
    util.parallel_execute(cr, util.explode_query_range(cr, query, table="crm_lead"))
