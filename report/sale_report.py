from odoo import fields, models


class SaleReport(models.Model):
    _inherit = "sale.report"

    sales_period_id = fields.Many2one(
        "sale_reporting_periods.sales_period",
        string="Sales Period",
        readonly=True,
    )

    def _query(self, with_clause="", fields={}, groupby="", from_clause=""):
        fields["sales_period_id"] = ", s.sales_period_id as sales_period_id"
        groupby += ", s.sales_period_id"
        return super()._query(with_clause, fields, groupby, from_clause)
