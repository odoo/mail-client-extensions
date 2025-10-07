import { buildLeadsView } from "./leads";
import { buildTasksView } from "./tasks";
import { buildTicketsView } from "./tickets";
import { buildPartnerActionView } from "./partner_actions";
import { createKeyValueWidget } from "./helpers";
import { getOdooServerUrl } from "src/services/app_properties";
import { State } from "../models/state";
import { _t } from "../services/translation";

export function buildPartnerView(state: State, card: Card) {
    const partner = state.partner;
    const odooServerUrl = getOdooServerUrl();

    const partnerSection = CardService.newCardSection().setHeader(
        "<b>" + _t("Contact Details") + "</b>",
    );

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

    const partnerCard = createKeyValueWidget(
        null,
        partner.name || partner.email || "",
        partner.getImage(),
        partnerContent.length ? partnerContent : null,
        null,
        null,
        false,
        partner.email,
        CardService.ImageCropType.CIRCLE,
    );

    partnerSection.addWidget(partnerCard);

    buildPartnerActionView(state, partnerSection);

    card.addSection(partnerSection);

    if (State.isLogged) {
        buildLeadsView(state, card);
        buildTicketsView(state, card);
        buildTasksView(state, card);
    }

    return card;
}
