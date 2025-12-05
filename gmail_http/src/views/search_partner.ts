import { ErrorMessage } from "../models/error_message";
import { Partner } from "../models/partner";
import { State } from "../models/state";
import { User } from "../models/user";
import { logEmail } from "../services/log_email";
import {
    ActionCall,
    EventResponse,
    Notify,
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
    Image,
    TextInput,
    TextParagraph,
} from "../utils/components";
import { buildCardActionsView } from "./card_actions";
import { UI_ICONS } from "./icons";
import { getPartnerView } from "./partner";
import { onEmailAlreadyLoggedContact } from "./partner_actions";

async function onSearchPartnerClick(
    state: State,
    _t: Function,
    user: User,
    args: Record<string, any>,
    formInputs: Record<string, any>,
): Promise<EventResponse> {
    const query = formInputs.search_partner_query || "";
    const [partners, error] =
        query && query.length ? await Partner.searchPartner(user, query) : [[], new ErrorMessage()];
    if (error.code) {
        return new Notify(error.message);
    }

    state.searchedPartners = partners;

    const card = await getSearchPartnerView(state, _t, user, query);
    return args.fixCard ? new PushCard(card) : new UpdateCard(card);
}
registerEventHandler(onSearchPartnerClick);

async function onLogEmailPartner(
    state: State,
    _t: Function,
    user: User,
    args: Record<string, any>,
    formInputs: Record<string, any>,
): Promise<EventResponse> {
    const partnerId = args.partnerId;

    if (!partnerId) {
        throw new Error(_t("This contact does not exist in the Odoo database."));
    }

    const error = await logEmail(_t, user, partnerId, "res.partner", state.email);
    if (error.code) {
        return new Notify(error.message);
    }
    await state.email.setLoggingState(user, "res.partner", partnerId);
    return new UpdateCard(await getSearchPartnerView(state, _t, user, args.query));
}
registerEventHandler(onLogEmailPartner);

async function onOpenPartner(
    state: State,
    _t: Function,
    user: User,
    args: Record<string, any>,
    formInputs: Record<string, any>,
): Promise<EventResponse> {
    const partner = Partner.fromJson(args.partner);
    const [newPartner, canCreatePartner, canCreateProject, error] = await Partner.getPartner(
        user,
        partner.name,
        partner.email,
        partner.id,
    );
    if (error.code) {
        return new Notify(error.message);
    }
    const newState = new State(
        newPartner,
        canCreatePartner,
        state.email,
        null,
        null,
        canCreateProject,
    );
    return new PushCard(getPartnerView(newState, _t, user));
}
registerEventHandler(onOpenPartner);

export async function getSearchPartnerView(
    state: State,
    _t: Function,
    user: User,
    query: string,
    initialSearch: boolean = false,
    header: string = "",
    noLogIcon: boolean = false,
    fixCard: boolean = false,
): Promise<Card> {
    const searchSection = new CardSection();
    const card = new Card([searchSection]);

    buildCardActionsView(card, _t);

    let partners = state.searchedPartners || [];
    let searchValue = query;

    if (initialSearch && partners.length <= 1) {
        partners = [];
        searchValue = "";
    }

    searchSection.addWidget(
        new TextInput(
            "search_partner_query",
            _t("Search contact"),
            new ActionCall(state, onSearchPartnerClick, { fixCard }),
            "",
            searchValue,
        ),
    );

    searchSection.addWidget(
        new Button(_t("Search"), new ActionCall(state, onSearchPartnerClick, { fixCard })),
    );

    if (header?.length) {
        searchSection.addWidget(new TextParagraph(`<b>${header}</b>`));
    }

    for (let partner of partners) {
        let button;
        let bottomLabel;

        if (partner.email) {
            bottomLabel = partner.id ? partner.email : _t("New Person");
        }

        if (partner.isWritable && !noLogIcon) {
            button = !state.email.checkLoggingState("res.partner", partner.id)
                ? new IconButton(
                      new ActionCall(state, onLogEmailPartner, {
                          partnerId: partner.id,
                          query: query,
                      }),
                      UI_ICONS.email_in_odoo,
                      _t("Log email"),
                  )
                : new IconButton(
                      new ActionCall(state, onEmailAlreadyLoggedContact),
                      UI_ICONS.email_logged,
                      _t("Email already logged on the contact"),
                  );
        }
        const partnerCard = new DecoratedText(
            undefined,
            partner.name,
            partner.getImage(),
            bottomLabel,
            button,
            new ActionCall(state, onOpenPartner, { partner }),
            true,
        );

        searchSection.addWidget(partnerCard);
    }

    if ((!partners || !partners.length) && !initialSearch) {
        const noRecord = btoa(
            atob(UI_ICONS.no_record)
                .replace("No record found.", _t("No record found."))
                .replace("Try using different keywords.", _t("Try using different keywords.")),
        );
        searchSection.addWidget(new Image("data:image/svg+xml;base64," + noRecord));
    }

    return card;
}
