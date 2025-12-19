import { State } from "../models/state";
import { Ticket } from "../models/ticket";
import { User } from "../models/user";
import { logEmail } from "../services/log_email";
import { getOdooRecordURL } from "../services/odoo_redirection";
import {
    ActionCall,
    EventResponse,
    Notify,
    OpenLink,
    PushCard,
    registerEventHandler,
    UpdateCard,
} from "../utils/actions";
import {
    Button,
    Card,
    CardSection,
    DecoratedText,
    IconButton,
    LinkButton,
} from "../utils/components";
import { getPartnerView } from "./partner";
import { getSearchRecordView } from "./search_records";

async function onCreateTicket(
    state: State,
    _t: Function,
    user: User,
    args: Record<string, any>,
    formInputs: Record<string, any>,
): Promise<EventResponse> {
    const result = await Ticket.createTicket(user, state.partner, state.email);

    if (!result) {
        return new Notify(_t("Could not create the ticket"));
    }

    const [ticket, partner] = result;
    state.partner = partner;
    state.partner.tickets.push(ticket);
    state.partner.ticketCount += 1;
    return new UpdateCard(getPartnerView(state, _t, user));
}
registerEventHandler(onCreateTicket);

function onSearchTicketsClick(
    state: State,
    _t: Function,
    user: User,
    args: Record<string, any>,
    formInputs: Record<string, any>,
): EventResponse {
    return new PushCard(
        getSearchRecordView(
            state,
            _t,
            "helpdesk.ticket",
            _t("Tickets"),
            _t("Log the email on the ticket"),
            _t("Email already logged on the ticket"),
            "",
            "",
            true,
            state.partner.tickets,
        ),
    );
}
registerEventHandler(onSearchTicketsClick);

async function onLogEmailOnTicket(
    state: State,
    _t: Function,
    user: User,
    args: Record<string, any>,
    formInputs: Record<string, any>,
): Promise<EventResponse> {
    const ticketId = args.ticketId;
    const error = await logEmail(_t, user, ticketId, "helpdesk.ticket", state.email);
    if (error.code) {
        return new Notify(error.toString(_t));
    }

    state.email.setLoggingState(user, "helpdesk.ticket", ticketId);
    return new UpdateCard(getPartnerView(state, _t, user));
}
registerEventHandler(onLogEmailOnTicket);

function onEmailAlreadyLoggedOnTicket(
    state: State,
    _t: Function,
    user: User,
    args: Record<string, any>,
    formInputs: Record<string, any>,
): EventResponse {
    return new Notify(_t("Email already logged on the ticket"));
}
registerEventHandler(onEmailAlreadyLoggedOnTicket);

export function buildTicketsView(state: State, _t: Function, user: User, card: Card) {
    const partner = state.partner;
    if (!partner.tickets) {
        // Helpdesk not installed
        // (otherwise we would have an empty array)
        return;
    }

    const tickets = [...partner.tickets].splice(0, 5);

    const ticketsSection = new CardSection();

    const searchButton = new IconButton(
        new ActionCall(state, onSearchTicketsClick),
        "/assets/search.png",
        _t("Search Tickets"),
    );

    const title = partner.ticketCount ? _t("Tickets (%s)", partner.ticketCount) : _t("Tickets");
    const widget = new DecoratedText(
        "",
        "<b>" + title + "</b>",
        undefined,
        undefined,
        searchButton,
    );
    ticketsSection.addWidget(widget);

    const createButton = new Button(_t("New"), new ActionCall(state, onCreateTicket));
    ticketsSection.addWidget(createButton);

    for (let ticket of tickets) {
        let ticketButton = null;
        if (state.email.checkLoggingState("helpdesk.ticket", ticket.id)) {
            ticketButton = new IconButton(
                new ActionCall(state, onEmailAlreadyLoggedOnTicket),
                "/assets/email_logged.png",
                _t("Email already logged on the ticket"),
            );
        } else {
            ticketButton = new IconButton(
                new ActionCall(state, onLogEmailOnTicket, {
                    ticketId: ticket.id,
                }),
                "/assets/email_in_odoo.png",
                _t("Log the email on the ticket"),
            );
        }

        ticketsSection.addWidget(
            new DecoratedText(
                "",
                ticket.name,
                undefined,
                ticket.stageName,
                ticketButton,
                new OpenLink(getOdooRecordURL(user, "helpdesk.ticket", ticket.id)),
            ),
        );
    }

    if (tickets.length < partner.ticketCount) {
        ticketsSection.addWidget(
            new LinkButton(_t("Show all"), new ActionCall(state, onSearchTicketsClick)),
        );
    }

    card.addSection(ticketsSection);
}
