import { Partner } from "../models/partner";
import { State } from "../models/state";
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
import { Button, ButtonsList, IconButton } from "../utils/components";
import { UI_ICONS } from "./icons";
import { getPartnerView } from "./partner";
import { getSearchPartnerView } from "./search_partner";

async function onLogEmail(state: State, _t: Function, user: User): Promise<EventResponse> {
    const partnerId = state.partner.id;

    if (!partnerId) {
        throw new Error(_t("This contact does not exist in the Odoo database."));
    }

    const error = await logEmail(_t, user, partnerId, "res.partner", state.email);
    if (error.code) {
        return new Notify(error.message);
    }
    state.email.setLoggingState(user, "res.partner", partnerId);
    return new UpdateCard(getPartnerView(state, _t, user));
}
registerEventHandler(onLogEmail);

async function onSavePartner(state: State, _t: Function, user: User): Promise<EventResponse> {
    const partner = await Partner.savePartner(user, state.partner);
    if (partner) {
        state.partner = partner;
        state.partner.isWritable = true;
        state.searchedPartners = null;
        return new UpdateCard(getPartnerView(state, _t, user));
    }
    return new Notify(_t("Can not save the contact"));
}
registerEventHandler(onSavePartner);

export function onEmailAlreadyLoggedContact(state: State, _t: Function, user: User): EventResponse {
    return new Notify(_t("Email already logged on the contact"));
}
registerEventHandler(onEmailAlreadyLoggedContact);

async function onSearchPartner(state: State, _t: Function, user: User): Promise<EventResponse> {
    state.searchedPartners = [];
    return new PushCard(await getSearchPartnerView(state, _t, user, state.partner.email, true));
}
registerEventHandler(onSearchPartner);

export function getPartnerActionButtons(state: State, _t: Function, user: User): ButtonsList {
    const actionButtonSet = new ButtonsList();

    const isEmailLogged =
        state.partner.id && state.email.checkLoggingState("res.partner", state.partner.id);

    if (!state.partner.id && state.canCreatePartner) {
        actionButtonSet.addButton(
            new Button(_t("Add to Odoo"), new ActionCall(state, onSavePartner), "#875a7b"),
        );
    }
    if (state.partner.id) {
        actionButtonSet.addButton(
            new Button(
                _t("View in Odoo"),
                new OpenLink(getOdooRecordURL(user, "res.partner", state.partner.id)),
                "#875a7b",
            ),
        );
    }
    if (state.partner.id && !isEmailLogged && state.partner.isWritable) {
        actionButtonSet.addButton(
            new IconButton(
                new ActionCall(state, onLogEmail),
                UI_ICONS.email_in_odoo,
                _t("Log email"),
            ),
        );
    }
    if (state.partner.id && isEmailLogged) {
        actionButtonSet.addButton(
            new IconButton(
                new ActionCall(state, onEmailAlreadyLoggedContact),
                UI_ICONS.email_logged,
                _t("Email already logged on the contact"),
            ),
        );
    }

    actionButtonSet.addButton(
        new IconButton(
            new ActionCall(state, onSearchPartner),
            UI_ICONS.search,
            _t("Search contact"),
        ),
    );

    return actionButtonSet;
}
