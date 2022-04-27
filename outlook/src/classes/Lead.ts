class Lead {
    id: number;
    name: string;
    expectedRevenue: string; // string because formatted
    probability: number;
    recurringRevenue?: string;
    recurringPlan?: string;

    static fromJSON(o: Object): Lead {
        const lead = new Lead();
        lead.id = o['lead_id'];
        lead.name = o['name'];
        lead.probability = o['probability'];

        lead.expectedRevenue = this.removeDecimals(o['expected_revenue']);

        if (o['recurring_revenue']) {
            lead.recurringRevenue = this.removeDecimals(o['recurring_revenue']);
            lead.recurringPlan = o['recurring_plan'];
        }

        return lead;
    }

    static copy(lead: Lead): Lead {
        const newLead = new Lead();
        newLead.id = lead.id;
        newLead.name = lead.name;
        newLead.expectedRevenue = lead.expectedRevenue;
        newLead.probability = lead.probability;
        return newLead;
    }

    private static removeDecimals(revenue: string): string {
        if (revenue.search(/\.00\D*$/) != -1) {
            // if it ends with ".00" or ".00 $" or ".00 €", etc.
            return revenue.replace(/\.00/, '');
        } else if (revenue.search(/,00\D*$/) != -1) {
            // if it ends with ",00" or ",00 $" or ",00 €", etc.
            return revenue.replace(/,00/, '');
        }
        return revenue;
    }
}

export default Lead;
