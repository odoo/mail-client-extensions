import { postJsonRpc } from "../utils/http";
import { URLS } from "../const";
import { getAccessToken } from "src/services/odoo_auth";

/**
 * Represent a "helpdesk.ticket" record.
 */
export class Ticket {
    id: number;
    name: string;

    /**
     * Make a RPC call to the Odoo database to create a ticket
     * and return the ID of the newly created record.
     */
    static createTicket(partnerId: number, emailBody: string, emailSubject: string): number {
        const url = PropertiesService.getUserProperties().getProperty("ODOO_SERVER_URL") + URLS.CREATE_TICKET;
        const odooAccessToken = getAccessToken();

        const response = postJsonRpc(
            url,
            { email_body: emailBody, email_subject: emailSubject, partner_id: partnerId },
            { Authorization: "Bearer " + odooAccessToken },
        );

        return response ? response.ticket_id || null : null;
    }

    /**
     * Unserialize the ticket object (reverse JSON.stringify).
     */
    static fromJson(values: any): Ticket {
        const ticket = new Ticket();
        ticket.id = values.id;
        ticket.name = values.name;
        return ticket;
    }

    /**
     * Parse the dictionary return by the Odoo endpoint.
     */
    static fromOdooResponse(values: any): Ticket {
        const ticket = new Ticket();
        ticket.id = values.ticket_id;
        ticket.name = values.name;
        return ticket;
    }
}
