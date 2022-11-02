from odoo import fields, models


class SaleReport(models.Model):
    _inherit = "sale.report"

    sales_period_id = fields.Many2one(
        "sale_reporting_periods.sales_period",
        string="Sales Period",
        readonly=True,
    )

    def _select_additional_fields(self):
        res = super()._select_additional_fields()
        res["sales_period_id"] = "s.sales_period_id"
        return res

    def _group_by_sale(self):
        return super()._group_by_sale() + ", s.sales_period_id"
