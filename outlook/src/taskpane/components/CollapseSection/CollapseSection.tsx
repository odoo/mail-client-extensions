import * as React from 'react';
import { faChevronDown, faChevronRight, faPlus } from '@fortawesome/free-solid-svg-icons';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import './CollapseSection.css';
import { ReactElement } from 'react';

type CollapseSectionProps = {
    title: string;
    isCollapsed: boolean;
    hasAddButton?: boolean;
    onAddButtonClick?: () => void;
    hideCollapseButton?: boolean;
    children: ReactElement;
    className?: string;
};

type CollapseSectionSate = {
    isCollapsed: boolean;
};

/***
 * Class which handles a collapsable section
 */
class CollapseSection extends React.Component<CollapseSectionProps, CollapseSectionSate> {
    constructor(props, context) {
        super(props, context);
        this.state = {
            isCollapsed: props.isCollapsed,
        };
    }

    private onCollapseButtonClick = () => {
        this.setState({ isCollapsed: !this.state.isCollapsed });
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

        return (
            <div className={`section-card ${this.props.className}`}>
                <div className="section-top">
                    <div className="section-title-text">{this.props.title}</div>
                    <div>
                        {addButton}
                        {collapseButton}
                    </div>
                </div>
                {!this.state.isCollapsed && this.props.children}
            </div>
        );
    }
}

export default CollapseSection;
