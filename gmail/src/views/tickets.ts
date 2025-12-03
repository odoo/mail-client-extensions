import { buildView } from "../views/index";
import { updateCard } from "./helpers";
import { UI_ICONS } from "./icons";
import { createKeyValueWidget, actionCall, notify, openUrl } from "./helpers";
import { getOdooServerUrl } from "src/services/app_properties";
import { State } from "../models/state";
import { Ticket } from "../models/ticket";
import { logEmail } from "../services/log_email";
import { _t } from "../services/translation";
import { getOdooRecordURL } from "src/services/odoo_redirection";
import { buildSearchRecordView } from "../views/search_records";

function onCreateTicket(state: State) {
    const result = Ticket.createTicket(state.partner, state.email);

    if (!result) {
        return notify(_t("Could not create the ticket"));
    }

    const [ticket, partner] = result;
    state.partner = partner;
    state.partner.tickets.push(ticket);
    state.partner.ticketCount += 1;
    return updateCard(buildView(state));
}

function onSearchClick(state: State) {
    return buildSearchRecordView(
        state,
        "helpdesk.ticket",
        _t("Tickets"),
        _t("Log the email on the ticket"),
        _t("Email already logged on the ticket"),
        "",
        "",
        true,
        state.partner.tickets,
    );
}

function onLogEmailOnTicket(state: State, parameters: any) {
    const ticketId = parameters.ticketId;

    if (State.checkLoggingState(state.email.messageId, "helpdesk.ticket", ticketId)) {
        const error = logEmail(ticketId, "helpdesk.ticket", state.email);
        if (error.code) {
            return notify(error.message);
        }

        State.setLoggingState(state.email.messageId, "helpdesk.ticket", ticketId);
        return updateCard(buildView(state));
    }
    return notify(_t("Email already logged on the ticket"));
}

function onEmailAlreadyLoggedOnTicket() {
    return notify(_t("Email already logged on the ticket"));
}

export function buildTicketsView(state: State, card: Card) {
    const odooServerUrl = getOdooServerUrl();
    const partner = state.partner;
    if (!partner.tickets) {
        // Helpdesk not installed
        // (otherwise we would have an empty array)
        return;
    }

    const tickets = [...partner.tickets].splice(0, 5);

    const loggingState = State.getLoggingState(state.email.messageId);

    const ticketsSection = CardService.newCardSection();

    const searchButton = CardService.newImageButton()
        .setAltText(_t("Search Tickets"))
        .setIconUrl(UI_ICONS.search)
        .setOnClickAction(actionCall(state, onSearchClick.name));

    const title = partner.ticketCount ? _t("Tickets (%s)", partner.ticketCount) : _t("Tickets");
    const widget = CardService.newDecoratedText().setText("<b>" + title + "</b>");
    widget.setButton(searchButton);
    ticketsSection.addWidget(widget);

    const createButton = CardService.newTextButton()
        .setText(_t("New"))
        .setOnClickAction(actionCall(state, onCreateTicket.name));
    ticketsSection.addWidget(createButton);

    for (let ticket of tickets) {
        let ticketButton = null;
        if (loggingState["helpdesk.ticket"].indexOf(ticket.id) >= 0) {
            ticketButton = CardService.newImageButton()
                .setAltText(_t("Email already logged on the ticket"))
                .setIconUrl(UI_ICONS.email_logged)
                .setOnClickAction(actionCall(state, onEmailAlreadyLoggedOnTicket.name));
        } else {
            ticketButton = CardService.newImageButton()
                .setAltText(_t("Log the email on the ticket"))
                .setIconUrl(UI_ICONS.email_in_odoo)
                .setOnClickAction(
                    actionCall(state, onLogEmailOnTicket.name, {
                        ticketId: ticket.id,
                    }),
                );
        }

        ticketsSection.addWidget(
            createKeyValueWidget(
                null,
                ticket.name,
                null,
                ticket.stageName,
                ticketButton,
                getOdooRecordURL("helpdesk.ticket", ticket.id),
            ),
        );
    }

    if (tickets.length < partner.ticketCount) {
        ticketsSection.addWidget(
            CardService.newTextButton()
                .setText(_t("Show all"))
                .setTextButtonStyle(CardService.TextButtonStyle["BORDERLESS"])
                .setOnClickAction(actionCall(state, onSearchClick.name)),
        );
    }

    card.addSection(ticketsSection);
    return card;
}
