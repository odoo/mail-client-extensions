import { State } from "../models/state";
import { User } from "../models/user";
import { logEmail } from "../services/log_email";
import { getOdooRecordURL } from "../services/odoo_redirection";
import { searchRecords } from "../services/search_records";
import {
    ActionCall,
    EventResponse,
    Notify,
    OpenLink,
    Redirect,
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
} from "../utils/components";
import { UI_ICONS } from "./icons";

async function onSearchRecordClick(
    state: State,
    _t: Function,
    user: User,
    args: Record<string, any>,
    formInputs: Record<string, any>,
): Promise<EventResponse> {
    const model = args.model;
    const modelDescription = args.modelDescription;
    const fieldInfo = args.fieldInfo;
    const query = formInputs.query || "";

    const [records, totalCount, error] = await searchRecords(user, model, query);
    if (error.code) {
        return new Notify(error.message);
    }
    return new UpdateCard(
        getSearchRecordView(
            state,
            _t,
            model,
            modelDescription,
            args.emailLogMessage,
            args.emailAlreadyLoggedMessage,
            fieldInfo,
            query,
            false,
            records,
            totalCount,
        ),
    );
}
registerEventHandler(onSearchRecordClick);

async function onLogEmailRecord(
    state: State,
    _t: Function,
    user: User,
    args: Record<string, any>,
    formInputs: Record<string, any>,
): Promise<EventResponse> {
    const model = args.model;
    const modelDescription = args.modelDescription;
    const fieldInfo = args.fieldInfo;
    const recordId = args.recordId;
    const records = args.records;
    const totalCount = args.totalCount;

    const error = await logEmail(_t, user, recordId, model, state.email);
    if (error.code) {
        return new Notify(error.message);
    }
    state.email.setLoggingState(user, model, recordId);
    return new UpdateCard(
        getSearchRecordView(
            state,
            _t,
            model,
            modelDescription,
            args.emailLogMessage,
            args.emailAlreadyLoggedMessage,
            fieldInfo,
            args.query,
            false,
            records,
            totalCount,
        ),
    );
}
registerEventHandler(onLogEmailRecord);

function onOpenRecord(
    state: State,
    _t: Function,
    user: User,
    args: Record<string, any>,
    formInputs: Record<string, any>,
): EventResponse {
    const model = args.model;
    const recordId = args.recordId;
    return new Redirect(new OpenLink(getOdooRecordURL(user, model, recordId)));
}
registerEventHandler(onOpenRecord);

function onEmailAlreadyLoggedOnRecord(
    state: State,
    _t: Function,
    user: User,
    args: Record<string, any>,
    formInputs: Record<string, any>,
): EventResponse {
    return new Notify(args.emailAlreadyLoggedMessage);
}
registerEventHandler(onEmailAlreadyLoggedOnRecord);

export function getSearchRecordView(
    state: State,
    _t: Function,
    model: string,
    modelDescription: string,
    emailLogMessage: string,
    emailAlreadyLoggedMessage: string,
    fieldInfo: string = "",
    query: string = "",
    initialSearch: boolean = false,
    records: any[] = [],
    totalCount: number = 0,
): Card {
    const searchSection = new CardSection();
    const card = new Card([searchSection]);
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

    searchSection.addWidget(
        new TextInput(
            "query",
            _t("Search %s", modelDescription),
            new ActionCall(state, onSearchRecordClick, baseArgs),
            "",
            searchValue,
        ),
    );

    searchSection.addWidget(
        new Button(_t("Search"), new ActionCall(state, onSearchRecordClick, baseArgs)),
    );

    for (let record of records) {
        const bottomLabel = fieldInfo?.length && record[fieldInfo] ? record[fieldInfo] : undefined;

        const button = !state.email.checkLoggingState(model, record.id)
            ? new IconButton(
                  new ActionCall(state, onLogEmailRecord, {
                      ...baseArgs,
                      recordId: record.id,
                      query,
                  }),
                  UI_ICONS.email_in_odoo,
                  emailLogMessage,
              )
            : new IconButton(
                  new ActionCall(state, onEmailAlreadyLoggedOnRecord, {
                      emailAlreadyLoggedMessage,
                  }),
                  UI_ICONS.email_logged,
                  emailAlreadyLoggedMessage,
              );

        const recordCard = new DecoratedText(
            "",
            record.name,
            undefined,
            undefined,
            button,
            new ActionCall(state, onOpenRecord, { model, recordId: record.id }),
            true,
        );

        searchSection.addWidget(recordCard);
    }

    if ((!records || !records.length) && !initialSearch) {
        const noRecord = btoa(
            atob(UI_ICONS.no_record)
                .replace("No record found.", _t("No record found."))
                .replace("Try using different keywords.", _t("Try using different keywords.")),
        );
        searchSection.addWidget(new Image("data:image/svg+xml;base64," + noRecord));
    }

    return card;
}
