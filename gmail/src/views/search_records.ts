import { logEmail } from "../services/log_email";
import { _t } from "../services/translation";
import { actionCall, updateCard, notify, openUrl } from "./helpers";
import { State } from "../models/state";
import { UI_ICONS } from "./icons";
import { getOdooRecordURL } from "src/services/odoo_redirection";
import { searchRecords } from "../services/search_records";

function onSearchRecordClick(state: State, parameters: any, inputs: any) {
    const model = parameters.model;
    const modelDescription = parameters.modelDescription;
    const fieldInfo = parameters.fieldInfo;
    const query = inputs.query || "";

    const [records, totalCount, error] = searchRecords(model, query);
    if (error.code) {
        return notify(error.message);
    }
    return updateCard(
        buildSearchRecordView(
            state,
            model,
            modelDescription,
            parameters.emailLogMessage,
            parameters.emailAlreadyLoggedMessage,
            fieldInfo,
            query,
            false,
            records,
            totalCount,
        ),
    );
}

function onLogEmailRecord(state: State, parameters: any) {
    const model = parameters.model;
    const modelDescription = parameters.modelDescription;
    const fieldInfo = parameters.fieldInfo;
    const recordId = parameters.recordId;
    const records = parameters.records;
    const totalCount = parameters.totalCount;

    if (State.checkLoggingState(state.email.messageId, model, recordId)) {
        const error = logEmail(recordId, model, state.email);
        if (error.code) {
            return notify(error.message);
        }
        State.setLoggingState(state.email.messageId, model, recordId);
        return updateCard(
            buildSearchRecordView(
                state,
                model,
                modelDescription,
                parameters.emailLogMessage,
                parameters.emailAlreadyLoggedMessage,
                fieldInfo,
                parameters.query,
                false,
                records,
                totalCount,
            ),
        );
    }
    return notify(_t("Email already logged"));
}

function onOpenRecord(state: State, parameters: any) {
    const model = parameters.model;
    const recordId = parameters.recordId;
    return openUrl(getOdooRecordURL(model, recordId));
}

function onEmailAlreadyLoggedOnRecord(parameters: any) {
    return notify(parameters.emailAlreadyLoggedMessage);
}

export function buildSearchRecordView(
    state: State,
    model: string,
    modelDescription: string,
    emailLogMessage: string,
    emailAlreadyLoggedMessage: string,
    fieldInfo: string = "",
    query: string = "",
    initialSearch: boolean = false,
    records: any[] = [],
    totalCount: number = 0,
) {
    const loggingState = State.getLoggingState(state.email.messageId);

    const card = CardService.newCardBuilder();
    let searchValue = query;

    const baseArgs = {
        model,
        modelDescription,
        fieldInfo,
        records,
        totalCount,
        emailAlreadyLoggedMessage,
        emailLogMessage,
    };

    const searchSection = CardService.newCardSection();

    searchSection.addWidget(
        CardService.newTextInput()
            .setFieldName("query")
            .setTitle(_t("Search %s", modelDescription))
            .setValue(searchValue)
            .setOnChangeAction(actionCall(state, onSearchRecordClick.name, baseArgs)),
    );

    searchSection.addWidget(
        CardService.newTextButton()
            .setText(_t("Search"))
            .setOnClickAction(actionCall(state, onSearchRecordClick.name, baseArgs)),
    );

    for (let record of records) {
        const recordCard = CardService.newDecoratedText()
            .setText(record.name)
            .setWrapText(true)
            .setOnClickAction(actionCall(state, onOpenRecord.name, { model, recordId: record.id }));

        if (fieldInfo?.length && record[fieldInfo]) {
            recordCard.setBottomLabel(record[fieldInfo]);
        }

        recordCard.setButton(
            loggingState[model].indexOf(record.id) < 0
                ? CardService.newImageButton()
                      .setAltText(emailLogMessage)
                      .setIconUrl(UI_ICONS.email_in_odoo)
                      .setOnClickAction(
                          actionCall(state, onLogEmailRecord.name, {
                              ...baseArgs,
                              recordId: record.id,
                              query,
                          }),
                      )
                : CardService.newImageButton()
                      .setAltText(emailAlreadyLoggedMessage)
                      .setIconUrl(UI_ICONS.email_logged)
                      .setOnClickAction(
                          actionCall(null, onEmailAlreadyLoggedOnRecord.name, {
                              emailAlreadyLoggedMessage,
                          }),
                      ),
        );

        searchSection.addWidget(recordCard);
    }

    if ((!records || !records.length) && !initialSearch) {
        const noRecord = Utilities.base64Encode(
            Utilities.newBlob(Utilities.base64Decode(UI_ICONS.no_record))
                .getDataAsString()
                .replace("No record found.", _t("No record found."))
                .replace("Try using different keywords.", _t("Try using different keywords.")),
        );
        searchSection.addWidget(
            CardService.newImage().setImageUrl("data:image/svg+xml;base64," + noRecord),
        );
    }

    card.addSection(searchSection);
    return card.build();
}
