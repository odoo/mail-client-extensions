/**
 * Represent a "helpdesk.ticket" record.
 */
var Ticket = /** @class */ (function () {
    function Ticket() {}
    /**
     * Make a RPC call to the Odoo database to create a ticket
     * and return the ID of the newly created record.
     */
    Ticket.createTicket = function (partnerId, emailBody, emailSubject) {
        var url = State.odooServerUrl + URLS.CREATE_TICKET;
        var accessToken = State.accessToken;
        var response = (0, postJsonRpc)(
            url,
            { email_body: emailBody, email_subject: emailSubject, partner_id: partnerId },
            { Authorization: "Bearer " + accessToken },
        );
        return response ? response.ticket_id || null : null;
    };
    /**
     * Unserialize the ticket object (reverse JSON.stringify).
     */
    Ticket.fromJson = function (values) {
        var ticket = new Ticket();
        ticket.id = values.id;
        ticket.name = values.name;
        return ticket;
    };
    /**
     * Parse the dictionary return by the Odoo endpoint.
     */
    Ticket.fromOdooResponse = function (values) {
        var ticket = new Ticket();
        ticket.id = values.ticket_id;
        ticket.name = values.name;
        return ticket;
    };
    return Ticket;
})();
