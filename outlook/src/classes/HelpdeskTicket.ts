class HelpdeskTicket {
    id: number;
    name: string;
    isClosed: boolean;

    static fromJSON(o: Object): HelpdeskTicket {
        const ticket = new HelpdeskTicket();
        ticket.id = o['ticket_id'];
        ticket.name = o['name'];
        ticket.isClosed = o['is_closed'];
        return ticket;
    }
}

export default HelpdeskTicket;
