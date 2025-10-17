import { Button, Image, makeStyles } from '@fluentui/react-components'
import * as React from 'react'
import { getOdooRecordURL } from '../../helpers/http'
import { _t } from '../../helpers/translate'
import { Partner } from '../../models/partner'
import { showError } from './Error'
import RecordCard from './RecordCard'

import {
    ArrowClockwiseRegular,
    BuildingRegular,
    MailRegular,
    PhoneRegular,
    SearchRegular,
    SignOutRegular,
} from '@fluentui/react-icons'
import { searchRecords } from '../../helpers/search_records'
import { Email } from '../../models/email'
import { Lead } from '../../models/lead'
import { Project } from '../../models/project'
import { Task } from '../../models/task'
import { Ticket } from '../../models/ticket'
import { hideGlobalLoading, showGlobalLoading } from './GlobalLoading'
import LogEmail from './LogEmail'
import RecordsSection from './RecordsSection'
import SearchRecords from './SearchRecords'
import SelectProject from './SelectProject'

export interface PartnerViewProps {
    partner: Partner
    email: Email
    onLogout: Function
    onSearch: Function
    pushPage: Function
    goBack: Function
    updatePartner: Function
}

const useStyles = makeStyles({
    title: {
        marginLeft: '5px',
        marginTop: '5px',
        marginBottom: '5px',
    },
    buttonsContainer: {
        display: 'flex',
        '& > *': {
            marginLeft: '5px',
        },
    },
    info: {
        display: 'flex',
        flexDirection: 'row',
        alignItems: 'center',
        '& > *': {
            // center the icons
            verticalAlign: 'middle',
        },
    },
    spinner: {
        padding: '4px',
    },
})

const PartnerView: React.FC<PartnerViewProps> = (props: PartnerViewProps) => {
    const {
        partner,
        email,
        onLogout,
        onSearch,
        pushPage,
        goBack,
        updatePartner,
    } = props
    const styles = useStyles()

    const [isRefreshing, setIsRefreshing] = React.useState(false)

    const onRefresh = async () => {
        setIsRefreshing(true)
        const [newPartner, error] = await Partner.getPartner(
            partner.name,
            partner.email,
            partner.id
        )
        setIsRefreshing(false)

        if (error.code) {
            showError(error.message)
            return
        }
        updatePartner(newPartner)
    }

    const onCreate = async () => {
        showGlobalLoading()
        const newPartner = await Partner.savePartner(partner)
        hideGlobalLoading()
        if (!newPartner) {
            showError(_t('Can not save the contact'))
            return
        }
        updatePartner(newPartner)
    }

    const onOpen = () => {
        window.open(getOdooRecordURL('res.partner', partner.id))
    }

    let description = []
    if (partner.companyName) {
        description.push(
            <span
                className={styles.info}
                key={`companyName-${partner.companyName}`}
            >
                <BuildingRegular /> {partner.companyName}
            </span>
        )
    }
    if (partner.email) {
        description.push(
            <span className={styles.info} key={`email-${partner.email}`}>
                <MailRegular /> {partner.email}
            </span>
        )
    }
    if (partner.phone) {
        description.push(
            <span className={styles.info} key={`phone-${partner.phone}`}>
                <PhoneRegular /> {partner.phone}
            </span>
        )
    }

    const onCreateLead = async () => {
        const result = await Lead.createLead(
            partner,
            await email.getBody(),
            email.subject
        )
        if (!result) {
            showError(_t('Could not create the opportunity'))
            return
        }
        const [record, newPartner] = result
        newPartner.leads.push(record)
        newPartner.leadCount += 1
        updatePartner(newPartner)
    }

    const onSearchLead = async () => {
        const onOpenLead = (lead) => {
            window.open(getOdooRecordURL('crm.lead', lead.id))
        }
        const searchLeads = async (query) => {
            const [records, _totalCount, error] = await searchRecords(
                'crm.lead',
                query
            )
            if (error.code) {
                return showError(error.message)
            }
            return records.map(Lead.fromOdooResponse)
        }
        pushPage(
            <SearchRecords
                onClick={onOpenLead}
                search={searchLeads}
                model="crm.lead"
                searchPlaceholder={_t('Search Opportunities')}
                records={partner.leads}
                nameAttribute="name"
                descriptionAttribute="revenuesDescription"
                email={email}
                logEmail={true}
                logEmailTitle={_t('Log the email on the opportunity')}
                logEmailAlreadyLogged={_t(
                    'Email already logged on the opportunity'
                )}
            />
        )
    }

    const onCreateTicket = async () => {
        const result = await Ticket.createTicket(
            partner,
            await email.getBody(),
            email.subject
        )
        if (!result) {
            showError(_t('Could not create the ticket'))
            return
        }
        const [record, newPartner] = result
        newPartner.tickets.push(record)
        newPartner.ticketCount += 1
        updatePartner(newPartner)
    }

    const onSearchTicket = async () => {
        const onOpenTicket = (ticket) => {
            window.open(getOdooRecordURL('helpdesk.ticket', ticket.id))
        }
        const searchTickets = async (query) => {
            const [records, _totalCount, error] = await searchRecords(
                'helpdesk.ticket',
                query
            )
            if (error.code) {
                return showError(error.message)
            }
            return records.map(Ticket.fromOdooResponse)
        }
        pushPage(
            <SearchRecords
                onClick={onOpenTicket}
                search={searchTickets}
                model="helpdesk.ticket"
                searchPlaceholder={_t('Search Tickets')}
                records={partner.tickets}
                nameAttribute="name"
                descriptionAttribute="stageName"
                email={email}
                logEmail={true}
                logEmailTitle={_t('Log the email on the ticket')}
                logEmailAlreadyLogged={_t('Email already logged on the ticket')}
            />
        )
    }

    const onCreateTask = async () => {
        const onSelectProject = async (
            project: Project,
            backCount: number = 1
        ) => {
            showGlobalLoading()
            const result = await Task.createTask(
                partner,
                project.id,
                await email.getBody(),
                email.subject
            )
            hideGlobalLoading()
            if (!result) {
                showError(_t('Could not create the task'))
                return
            }
            const [record, newPartner] = result
            newPartner.tasks.push(record)
            newPartner.taskCount += 1
            goBack(backCount)
            updatePartner(newPartner)
        }
        pushPage(
            <SelectProject
                canCreateProject={partner.canCreateProject}
                onSelectProject={onSelectProject}
                pushPage={pushPage}
            />
        )
    }

    const onSearchTask = async () => {
        const onOpenTask = (task) => {
            window.open(getOdooRecordURL('project.task', task.id))
        }
        const searchTasks = async (query) => {
            const [records, _totalCount, error] = await searchRecords(
                'project.task',
                query
            )
            if (error.code) {
                return showError(error.message)
            }
            return records.map(Task.fromOdooResponse)
        }
        pushPage(
            <SearchRecords
                onClick={onOpenTask}
                search={searchTasks}
                model="project.task"
                searchPlaceholder={_t('Search Tasks')}
                records={partner.tasks}
                nameAttribute="name"
                descriptionAttribute="projectName"
                email={email}
                logEmail={true}
                logEmailTitle={_t('Log the email on the task')}
                logEmailAlreadyLogged={_t('Email already logged on the task')}
            />
        )
    }

    return (
        <div>
            <h4 className={styles.title}>{_t('Contact Details')}</h4>
            <RecordCard
                model="res.partner"
                record={partner}
                description={description}
                icon={partner.image}
                name={partner.name}
                email={email}
            />
            <div className={styles.buttonsContainer}>
                {!partner.id && partner.canCreatePartner && (
                    <Button
                        appearance="primary"
                        size="small"
                        shape="circular"
                        onClick={onCreate}
                    >
                        {_t('Add to Odoo')}
                    </Button>
                )}
                {partner.id && (
                    <Button
                        appearance="primary"
                        size="small"
                        shape="circular"
                        onClick={onOpen}
                    >
                        {_t('View in Odoo')}
                    </Button>
                )}
                {partner.id && partner.isWritable && (
                    <LogEmail
                        recordId={partner.id}
                        model={'res.partner'}
                        email={email}
                        logEmailTitle={_t('Log email')}
                        logEmailAlreadyLogged={_t(
                            'Email already logged on the contact'
                        )}
                    />
                )}

                {isRefreshing ? (
                    <Image
                        className={styles.spinner}
                        width="24px"
                        src="assets/spinner.gif"
                        alt={_t('Loading')}
                    />
                ) : (
                    <Button
                        icon={<ArrowClockwiseRegular />}
                        title={_t('Refresh Contact Details')}
                        size="small"
                        shape="circular"
                        appearance="subtle"
                        onClick={onRefresh}
                    />
                )}
                <Button
                    icon={<SearchRegular />}
                    title={_t('Search contact')}
                    size="small"
                    shape="circular"
                    appearance="subtle"
                    onClick={() => onSearch()}
                />
                <Button
                    icon={<SignOutRegular />}
                    title={_t('Logout')}
                    size="small"
                    shape="circular"
                    appearance="subtle"
                    onClick={() => onLogout()}
                />
            </div>
            {!!partner.leads && (
                <RecordsSection
                    email={email}
                    model="crm.lead"
                    descriptionAttribute="revenuesDescription"
                    logEmailTitle={_t('Log the email on the opportunity')}
                    logEmailAlreadyLogged={_t(
                        'Email already logged on the opportunity'
                    )}
                    searchTitle={_t('Search Opportunities')}
                    sectionTitle={
                        partner.leadCount
                            ? _t('Opportunities (%s)', partner.leadCount)
                            : _t('Opportunities')
                    }
                    records={partner.leads}
                    recordCount={partner.leadCount}
                    createRecord={onCreateLead}
                    onSearch={onSearchLead}
                />
            )}
            {!!partner.tickets && (
                <RecordsSection
                    email={email}
                    model="helpdesk.ticket"
                    descriptionAttribute="stageName"
                    logEmailTitle={_t('Log the email on the ticket')}
                    logEmailAlreadyLogged={_t(
                        'Email already logged on the ticket'
                    )}
                    searchTitle={_t('Search Tickets')}
                    sectionTitle={
                        partner.ticketCount
                            ? _t('Tickets (%s)', partner.ticketCount)
                            : _t('Tickets')
                    }
                    records={partner.tickets}
                    recordCount={partner.ticketCount}
                    createRecord={onCreateTicket}
                    onSearch={onSearchTicket}
                />
            )}
            {!!partner.tasks && (
                <RecordsSection
                    email={email}
                    model="project.task"
                    descriptionAttribute="projectName"
                    logEmailTitle={_t('Log the email on the task')}
                    logEmailAlreadyLogged={_t(
                        'Email already logged on the task'
                    )}
                    searchTitle={_t('Search Tasks')}
                    sectionTitle={
                        partner.taskCount
                            ? _t('Tasks (%s)', partner.taskCount)
                            : _t('Tasks')
                    }
                    records={partner.tasks}
                    recordCount={partner.taskCount}
                    createRecord={onCreateTask}
                    onSearch={onSearchTask}
                />
            )}
        </div>
    )
}

export default PartnerView
