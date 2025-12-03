import { buildView } from "../views/index";
import { updateCard } from "./helpers";
import { UI_ICONS } from "./icons";
import { createKeyValueWidget, actionCall, notify, openUrl } from "./helpers";
import { URLS } from "../const";
import { getOdooServerUrl } from "src/services/app_properties";
import { State } from "../models/state";
import { Ticket } from "../models/ticket";
import { logEmail } from "../services/log_email";
import { _t } from "../services/translation";

function onCreateTicket(state: State) {
    const ticketId = Ticket.createTicket(state.partner.id, state.email.body, state.email.subject);

    if (!ticketId) {
        return notify(_t("Could not create the ticket"));
    }

    const cids = state.odooCompaniesParameter;

    const ticketUrl =
        PropertiesService.getUserProperties().getProperty("ODOO_SERVER_URL") +
        `/web#id=${ticketId}&action=helpdesk_mail_plugin.helpdesk_ticket_action_form_edit&model=helpdesk.ticket&view_type=form${cids}`;

    return openUrl(ticketUrl);
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

function onEmailAlreradyLoggedOnTicket() {
    return notify(_t("Email already logged on the ticket"));
}

export function buildTicketsView(state: State, card: Card) {
    const odooServerUrl = getOdooServerUrl();
    const partner = state.partner;
    const tickets = partner.tickets;

    if (!tickets) {
        return;
    }

    const loggingState = State.getLoggingState(state.email.messageId);

    const ticketsSection = CardService.newCardSection().setHeader("<b>" + _t("Tickets (%s)", tickets.length) + "</b>");

    if (state.partner.id) {
        ticketsSection.addWidget(
            CardService.newTextButton().setText(_t("Create")).setOnClickAction(actionCall(state, onCreateTicket.name)),
        );

        const cids = state.odooCompaniesParameter;

        for (let ticket of tickets) {
            let ticketButton = null;
            if (loggingState["tickets"].indexOf(ticket.id) >= 0) {
                ticketButton = CardService.newImageButton()
                    .setAltText(_t("Email already logged on the ticket"))
                    .setIconUrl(UI_ICONS.email_logged)
                    .setOnClickAction(actionCall(state, onEmailAlreradyLoggedOnTicket.name));
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
                    odooServerUrl + `/web#id=${ticket.id}&model=helpdesk.ticket&view_type=form${cids}`,
                ),
            );
        }
    } else if (state.canCreatePartner) {
        ticketsSection.addWidget(CardService.newTextParagraph().setText(_t("Save the contact to create new tickets.")));
    } else {
        ticketsSection.addWidget(
            CardService.newTextParagraph().setText(_t("The Contact needs to exist to create Ticket.")),
        );
    }

    card.addSection(ticketsSection);
    return card;
}
