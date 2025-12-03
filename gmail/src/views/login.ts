import { formatUrl } from "../utils/format";
import { notify } from "./helpers";
import { State } from "../models/state";
import { IMAGES_LOGIN } from "./icons";
import { getSupportedAddinVersion } from "../services/odoo_auth";
import { _t, clearTranslationCache } from "../services/translation";
import { setOdooServerUrl } from "src/services/app_properties";

function onNextLogin(event) {
    let domain = null;
    try {
        domain = new URL(formatUrl(event.formInputs.odooServerUrl)).origin;
    } catch {}
    if (!domain) {
        return notify(`Invalid URL ${event.formInputs.odooServerUrl}`);
    }

    if (!/^https:\/\/([^\/?]*\.)?odoo\.com(\/|$)/.test(domain)) {
        return notify(
            "The URL must be a subdomain of odoo.com, see the <a href='https://www.odoo.com/documentation/master/applications/general/integrations/mail_plugins/gmail.html'>documentation</a>",
        );
    }

    clearTranslationCache();

    setOdooServerUrl(domain);

    const version = getSupportedAddinVersion(domain);

    if (!version) {
        return notify("Could not connect to your database.");
    }

    if (version !== 2) {
        return notify(
            "This addin version required Odoo 19.2 or a newer version, please install an older addin version.",
        );
    }

    return CardService.newActionResponseBuilder()
        .setOpenLink(
            CardService.newOpenLink()
                .setUrl(State.odooLoginUrl)
                .setOpenAs(CardService.OpenAs.OVERLAY)
                .setOnClose(CardService.OnClose.RELOAD),
        )
        .build();
}

export function buildLoginMainView(error: string = null) {
    const card = CardService.newCardBuilder();

    const loginButton = Utilities.base64Encode(
        Utilities.newBlob(Utilities.base64Decode(IMAGES_LOGIN.buttonSVG))
            .getDataAsString()
            .replace("__TEXT__", "Login")
            .replace("__STROKE__", "#875a7b")
            .replace("__FILL__", "#875a7b")
            .replace("__COLOR__", "white"),
    );

    const signupButton = Utilities.base64Encode(
        Utilities.newBlob(Utilities.base64Decode(IMAGES_LOGIN.buttonSVG))
            .getDataAsString()
            .replace("__TEXT__", "Sign Up")
            .replace("__STROKE__", "#e7e9ed")
            .replace("__FILL__", "#e7e9ed")
            .replace("__COLOR__", "#1e1e1e"),
    );

    const faqButton = Utilities.base64Encode(
        Utilities.newBlob(Utilities.base64Decode(IMAGES_LOGIN.buttonSVG))
            .getDataAsString()
            .replace("__TEXT__", "FAQ")
            .replace("__STROKE__", "white")
            .replace("__FILL__", "white")
            .replace("__COLOR__", "#2f9e44"),
    );

    const section = CardService.newCardSection()
        .addWidget(
            CardService.newImage()
                .setAltText("Connect to your Odoo database")
                .setImageUrl(IMAGES_LOGIN.loginSVG),
        )
        .addWidget(
            CardService.newTextInput()
                .setFieldName("odooServerUrl")
                .setTitle("Connect to...")
                .setHint("e.g. company.odoo.com")
                .setValue(
                    PropertiesService.getUserProperties().getProperty("ODOO_SERVER_URL") || "",
                )
                .setOnChangeAction(CardService.newAction().setFunctionName(onNextLogin.name)),
        )
        .addWidget(
            CardService.newImage()
                .setImageUrl("data:image/svg+xml;base64," + loginButton)
                .setOnClickAction(CardService.newAction().setFunctionName(onNextLogin.name)),
        )
        .addWidget(
            CardService.newImage()
                .setImageUrl("data:image/svg+xml;base64," + signupButton)
                .setOpenLink(
                    CardService.newOpenLink().setUrl(
                        "https://www.odoo.com/trial?selected_app=mail_plugin:crm:helpdesk:project",
                    ),
                ),
        )
        .addWidget(
            CardService.newImage()
                .setImageUrl("data:image/svg+xml;base64," + faqButton)
                .setOpenLink(
                    CardService.newOpenLink().setUrl(
                        "https://www.odoo.com/documentation/master/applications/productivity/mail_plugins.html",
                    ),
                ),
        );

    if (error) {
        section.addWidget(CardService.newTextParagraph().setText(error));
    }

    card.addSection(section);

    return card.build();
}
