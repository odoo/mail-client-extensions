import * as React from "react";
import { FocusZone, FocusZoneDirection } from "office-ui-fabric-react/lib/FocusZone";
import { List } from "office-ui-fabric-react/lib/List";
import { ITheme, mergeStyleSets, getTheme, getFocusStyle } from "office-ui-fabric-react/lib/Styling";
import AppContext from "../AppContext";

type CompanyInsightsProps = {};
type CompanyInsightsState = {};

interface IListGhostingExampleClassObject {
  container: string;
  itemCell: string;
  itemImage: string;
  itemContent: string;
  itemName: string;
  itemIndex: string;
  chevron: string;
  itemButton: string;
}

const theme: ITheme = getTheme();
const { palette, semanticColors, fonts } = theme;

const classNames: IListGhostingExampleClassObject = mergeStyleSets({
  container: {
    /*
    overflow: 'auto',
    maxHeight: 200*/
  },
  itemCell: [
    getFocusStyle(theme, { inset: -1 }),
    {
      minHeight: 54,
      padding: 10,
      boxSizing: "border-box",
      borderBottom: `1px solid ${semanticColors.bodyDivider}`,
      display: "flex",
      /*cursor: 'pointer',*/
      selectors: {
        "&:hover .CompanyInsightValue": {
          whiteSpace: "normal",
          overflow: "visible",
          textOverflow: "-",
          overflowWrap: "break-word"
        }
      }
    }
  ],
  itemImage: {
    flexShrink: 0
  },
  itemContent: {
    /*marginLeft: 10,*/
    overflow: "hidden",
    flexGrow: 1
  },
  itemName: {
    fontSize: fonts.small.fontSize,
    color: palette.neutralTertiary
  },
  itemButton: {
    display: "none",
    marginLeft: "1em"
  },
  itemIndex: [
    fonts.medium,
    {
      whiteSpace: "nowrap",
      overflow: "hidden",
      textOverflow: "ellipsis"
    }
    /*marginBottom: 10*/
  ],
  chevron: {
    alignSelf: "center",
    marginLeft: 10,
    color: palette.neutralTertiary,
    fontSize: fonts.large.fontSize,
    flexShrink: 0
  }
});

class CompanyInsights extends React.Component<CompanyInsightsProps, CompanyInsightsState> {
  constructor(props) {
    super(props);
  }

  public render(): JSX.Element {
    const { company } = this.context.partner;
    let items = [
        { title: "Industry", value: company.getIndustry() },
        { title: "Employees", value: company.getEmployees() },
        { title: "Year Founded", value: company.getYearFounded() },
        { title: "Keywords", value: company.getKeywords() },
        { title: "Company Type", value: company.getCompanyType() },
        { title: "Revenue", value: company.getRevenue() }
    ];

    items = items.filter(x => x.value)
    if (!items.length)
      return null;

    return (
      <div className='bounded-tile'>
        <div className="company-insights">
            <FocusZone direction={FocusZoneDirection.vertical}>
                <div className={classNames.container} data-is-scrollable={true}>
                <List items={items} onRenderCell={this._onRenderCell} />
                </div>
            </FocusZone>
        </div>
      </div>
    );
    }

  private _onRenderCell = (item): JSX.Element => {
    if (item.value) {
        return (
            <div className={classNames.itemCell} data-is-focusable={true}>
                <div className={classNames.itemContent}>
                    <div className={classNames.itemName}>{item.title}</div>
                    <div className={`CompanyInsightValue ${classNames.itemIndex}`}>{item.value}</div>
                </div>
            </div>
        );
    }
    return null;
    };
}

CompanyInsights.contextType = AppContext;
export default CompanyInsights;
