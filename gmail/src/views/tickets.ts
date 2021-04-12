import { buildView } from "../views/index";
import { updateCard } from "./helpers";
import { UI_ICONS } from "./icons";
import { createKeyValueWidget, actionCall, notify, openUrl } from "./helpers";
import { URLS } from "../const";
import { State } from "../models/state";
import { Ticket } from "../models/ticket";
import { logEmail } from "../services/log_email";
import { _t } from "../services/translation";

function onCreateTicket(state: State) {
    const ticketId = Ticket.createTicket(state.partner.id, state.email.body, state.email.subject);

    if (!ticketId) {
        return notify("Could not create the ticket");
    }

    const ticketUrl =
        State.odooServerUrl +
        `/web#id=${ticketId}&action=helpdesk_mail_plugin.helpdesk_ticket_action_form_edit&model=helpdesk.ticket&view_type=form`;

    return openUrl(ticketUrl);
}

function onLogEmailOnTicket(state: State, parameters: any) {
    const emailBody = state.email.body;
    const ticketId = parameters.ticketId;

    if (State.setLoggingState(state.email.messageId, "tickets", ticketId)) {
        logEmail(ticketId, "helpdesk.ticket", emailBody);
        return updateCard(buildView(state));
    }
    return notify(_t("Email already logged on the ticket"));
}

function onEmailAlreradyLoggedOnTicket() {
    return notify(_t("Email already logged on the ticket"));
}

export function buildTicketsView(state: State, card: Card) {
    const odooServerUrl = State.odooServerUrl;
    const partner = state.partner;
    const tickets = partner.tickets;

    if (!tickets) {
        return;
    }

    const loggingState = State.getLoggingState(state.email.messageId);

    const ticketsSection = CardService.newCardSection().setHeader("<b>" + _t("Tickets (%s)", tickets.length) + "</b>");

    if (state.partner.id) {
        ticketsSection.addWidget(
            CardService.newTextButton().setText(_t("Create")).setOnClickAction(actionCall(state, "onCreateTicket")),
        );

        for (let ticket of tickets) {
            let ticketButton = null;
            if (loggingState["tickets"].indexOf(ticket.id) >= 0) {
                ticketButton = CardService.newImageButton()
                    .setAltText(_t("Email already logged on the ticket"))
                    .setIconUrl(UI_ICONS.email_logged)
                    .setOnClickAction(actionCall(state, "onEmailAlreradyLoggedOnTicket"));
            } else {
                ticketButton = CardService.newImageButton()
                    .setAltText(_t("Log the email on the ticket"))
                    .setIconUrl(UI_ICONS.email_in_odoo)
                    .setOnClickAction(
                        actionCall(state, "onLogEmailOnTicket", {
                            ticketId: ticket.id,
                        }),
                    );
            }

            ticketsSection.addWidget(
                createKeyValueWidget(
                    null,
                    ticket.name,
                    null,
                    null,
                    ticketButton,
                    odooServerUrl + `/web#id=${ticket.id}&model=helpdesk.ticket&view_type=form`,
                ),
            );
        }
    } else {
        ticketsSection.addWidget(CardService.newTextParagraph().setText(_t("Save the contact to create new tickets.")));
    }

    card.addSection(ticketsSection);
    return card;
}
