import { postJsonRpc } from "../utils/http";
import { URLS } from "../const";
import { getAccessToken } from "src/services/odoo_auth";
import { Partner } from "./partner";

/**
 * Represent a "helpdesk.ticket" record.
 */
export class Ticket {
    id: number;
    name: string;
    stageName: string;

    /**
     * Make a RPC call to the Odoo database to create a ticket
     * and return the ID of the newly created record.
     */
    static createTicket(
        partner: Partner,
        emailBody: string,
        emailSubject: string,
    ): [Ticket, Partner] | null {
        const url =
            PropertiesService.getUserProperties().getProperty("ODOO_SERVER_URL") +
            URLS.CREATE_TICKET;
        const odooAccessToken = getAccessToken();

        const response = postJsonRpc(
            url,
            {
                email_body: emailBody,
                email_subject: emailSubject,
                partner_email: partner.email,
                partner_id: partner.id,
                partner_name: partner.name,
            },
            { Authorization: "Bearer " + odooAccessToken },
        );

        if (!response?.id) {
            return null;
        }
        if (!partner.id) {
            partner.id = response.partner_id;
            partner.image = response.partner_image;
            partner.isWritable = true;
        }
        return [Ticket.fromOdooResponse(response), partner];
    }

    /**
     * Unserialize the ticket object (reverse JSON.stringify).
     */
    static fromJson(values: any): Ticket {
        const ticket = new Ticket();
        ticket.id = values.id;
        ticket.name = values.name;
        ticket.stageName = values.stageName;
        return ticket;
    }

    /**
     * Parse the dictionary return by the Odoo endpoint.
     */
    static fromOdooResponse(values: any): Ticket {
        const ticket = new Ticket();
        ticket.id = values.id;
        ticket.name = values.name;
        ticket.stageName = values.stage_name;
        return ticket;
    }
}
