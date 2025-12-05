import { Partner } from "../models/partner";
import { State } from "../models/state";
import { User } from "../models/user";
import {
    ActionCall,
    EventResponse,
    Notify,
    registerEventHandler,
    UpdateCard,
} from "../utils/actions";
import { Card, CardSection, DecoratedText } from "../utils/components";
import { buildCardActionsView } from "./card_actions";
import { buildLeadsView } from "./leads";
import { getPartnerActionButtons } from "./partner_actions";
import { buildTasksView } from "./tasks";
import { buildTicketsView } from "./tickets";

export async function onReloadPartner(
    state: State,
    _t: Function,
    user: User,
): Promise<EventResponse> {
    const values = await Partner.getPartner(
        user,
        state.partner.name,
        state.partner.email,
        state.partner.id,
    );

    [state.partner, state.canCreatePartner, state.canCreateProject] = values;

    if (values[3].code) {
        return new Notify(values[3].message);
    }
    return new UpdateCard(getPartnerView(state, _t, user));
}
registerEventHandler(onReloadPartner);

export function getPartnerView(state: State, _t: Function, user: User): Card {
    const section = new CardSection();
    const card = new Card([section]);
    buildCardActionsView(card, _t);
    card.addAction(_t("Refresh"), new ActionCall(state, onReloadPartner));

    const partner = state.partner;

    section.setHeader("<b>" + _t("Contact Details") + "</b>");

    let partnerContent = [
        partner.companyName && `🏢 ${partner.companyName}`,
        partner.email && `✉️ ${partner.email}`,
        partner.phone && `📞 ${partner.phone}`,
    ]
        .filter((x) => x)
        .map((x) => `<font color="#777777">${x}</font>`)
        .join("<br>");
    if (!partner.id) {
        partnerContent = _t("New Person");
    }

    const partnerCard = new DecoratedText(
        null,
        partner.name || partner.email || "",
        partner.getImage(),
        partnerContent.length ? partnerContent : null,
        null,
        null,
        false,
        partner.email,
    );

    section.addWidget(partnerCard);

    section.addWidget(getPartnerActionButtons(state, _t, user));

    buildLeadsView(state, _t, user, card);
    buildTicketsView(state, _t, user, card);
    buildTasksView(state, _t, user, card);

    return card;
}
