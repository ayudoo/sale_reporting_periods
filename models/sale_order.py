import logging
from odoo import api, fields, models
from odoo.osv import expression

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _get_sales_period_base_domain(self):
        date_domain = [
            ("assignment_time", "=", "create_date"),
            ("|"),
            ("date_from", "<=", self.create_date),
            ("date_from", "=", False),
            ("|"),
            ("date_to", ">=", self.create_date),
            ("date_to", "=", False),
        ]

        if self.state in ["sale", "done"] and self.date_order:
            date_domain = expression.OR(
                [
                    date_domain,
                    [
                        ("assignment_time", "=", "order_date"),
                        ("|"),
                        ("date_from", "<=", self.date_order),
                        ("date_from", "=", False),
                        ("|"),
                        ("date_to", ">=", self.date_order),
                        ("date_to", "=", False),
                    ],
                ]
            )

        return expression.AND(
            [[("assign_to", "in", ["all", "condition"])], date_domain]
        )

    def _get_default_sales_period(self):
        SalesPeriod = self.env["sale_reporting_periods.sales_period"]
        domain = self._get_sales_period_base_domain()

        # There is not reverse-domain match. So, we match by date and check the
        # results if this sales order matches their condition.
        eligible = SalesPeriod.search(domain)
        for sales_period in eligible:
            if sales_period.assign_to == "all":
                return sales_period

            try:
                if not sales_period.order_domain:
                    continue

                order_domain = sales_period._parse_order_domain()
                order_domain.append(("id", "=", self.id))
                if self.env["sale.order"].search(order_domain).exists():
                    return sales_period

            except ValueError:
                # if a domain is outdated, we don't want to break sale orders
                _logger.warning(
                    "Sales Period '{}' (#{}) has an outdated domain".format(
                        sales_period.name, sales_period.id
                    )
                )

        return False

    def _set_default_sales_periods(self, recompute=False):
        for record in self:
            if not record.sales_period_id or recompute:
                if record.state in ["draft", "sale", "done"]:
                    default = record._get_default_sales_period()
                    if default:
                        record.sales_period_id = default
                    elif not default and record.sales_period_id:
                        record.sales_period_id = default

    sales_period_id = fields.Many2one(
        "sale_reporting_periods.sales_period",
        string="Sales Period",
        # compute=_compute_sales_period,
        readonly=False,
        store=True,
    )

    @api.model
    def create(self, values):
        record = super().create(values)
        record._set_default_sales_periods()
        return record

    def write(self, values):
        r = super().write(values)
        self._set_default_sales_periods()
        return r

    @api.model
    def search_count(self, args):
        assignment_time = self.env.context.get("preview_sales_period_assignment_time")
        date_from = self.env.context.get("preview_sales_period_date_from")
        date_to = self.env.context.get("preview_sales_period_date_to")

        if assignment_time:
            args = args + self.env[
                "sale_reporting_periods.sales_period"
            ]._get_base_domain(assignment_time, date_from, date_to)
        return super().search_count(args)
