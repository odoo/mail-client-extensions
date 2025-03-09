import * as React from 'react';
import { faChevronDown, faChevronRight, faPlus } from '@fortawesome/free-solid-svg-icons';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import './CollapseSection.css';
import { ReactElement } from 'react';
import HelpdeskTicket from '../../../classes/HelpdeskTicket';
import Lead from '../../../classes/Lead';
import Partner from '../../../classes/Partner';
import SearchRefrech from '../SearchRefrech/SearchRefrech';
import Task from '../../../classes/Task';

type CollapseSectionProps = {
    title: string;
    isCollapsed: boolean;
    hasAddButton?: boolean;
    onAddButtonClick?: () => void;
    hideCollapseButton?: boolean;
    children: ReactElement;
    className?: string;
    partner?: Partner;
    searchType?: 'lead' | 'task' | 'ticket';
    setIsLoading?: (isLoading: boolean) => void;
    updateRecords?: (records: Lead[] | Task[] | HelpdeskTicket[]) => void;
};

type CollapseSectionSate = {
    isCollapsed: boolean;
    isSearching: boolean;
};

/***
 * Class which handles a collapsable section
 */
class CollapseSection extends React.Component<CollapseSectionProps, CollapseSectionSate> {
    constructor(props, context) {
        super(props, context);
        this.state = {
            isCollapsed: props.isCollapsed,
            isSearching: false,
        };
    }

    private onCollapseButtonClick = () => {
        this.setState({ isCollapsed: !this.state.isCollapsed });
    };

    private setIsSearching = (isSearching: boolean) => {
        this.setState({ isSearching });
    };

    render() {
        const addButton = this.props.hasAddButton && (
            <FontAwesomeIcon icon={faPlus} className="collapse-section-button" onClick={this.props.onAddButtonClick} />
        );

        const collapseButton = !this.props.hideCollapseButton && (
            <FontAwesomeIcon
                className="collapse-section-button"
                icon={this.state.isCollapsed ? faChevronRight : faChevronDown}
                onClick={this.onCollapseButtonClick}
            />
        );

        const searchRefrech = this.props.searchType && (
            <SearchRefrech
                title={this.props.title}
                partner={this.props.partner}
                searchType={this.props.searchType}
                setIsSearching={this.setIsSearching}
                setIsLoading={this.props.setIsLoading}
                updateRecords={this.props.updateRecords}
            />
        );

        return (
            <div className={`section-card ${this.props.className}`}>
                <div className="section-top">
                    {!this.state.isSearching && <div className="section-title-text">{this.props.title}</div>}
                    <div style={{ display: 'flex' }}>
                        {searchRefrech}
                        {!this.state.isSearching && (
                            <>
                                {addButton}
                                {collapseButton}
                            </>
                        )}
                    </div>
                </div>
                {!this.state.isCollapsed && this.props.children}
            </div>
        );
    }
}

export default CollapseSection;
