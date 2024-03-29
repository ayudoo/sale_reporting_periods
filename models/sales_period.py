from ast import literal_eval
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SalesPeriod(models.Model):
    _name = "sale_reporting_periods.sales_period"
    _description = "Sales Period"
    _order = "sequence, name"

    _sql_constraints = [
        ("unique_name", "UNIQUE(name)", "The name already exists"),
    ]

    name = fields.Char(translate=True, required=True)

    sequence = fields.Integer("Sequence")
    active = fields.Boolean(
        default=True,
        help="If the active field is set to false, it will allow you to hide"
        + " it without removing it.",
    )

    sale_order_ids = fields.One2many(
        "sale.order",
        "sales_period_id",
        string="Sales Orders",
        readonly=True,
    )

    def _compute_sale_order_count(self):
        for record in self:
            record.sale_order_count = len(record.sale_order_ids)

    sale_order_count = fields.Integer(
        string="Sales Order Count",
        compute=_compute_sale_order_count,
    )

    date_from = fields.Datetime(
        string="Date From",
    )
    date_to = fields.Datetime(
        string="Date To",
    )

    @api.constrains("date_from", "date_to")
    def check_dates(self):
        if self.filtered(
            lambda r: r.date_from and r.date_to and r.date_from > r.date_to
        ):
            raise ValidationError(
                _("The start date must be earlier than the end date.")
            )

    assign_to = fields.Selection(
        [
            ("none", "None"),
            ("all", "All"),
            ("condition", "Complex Condition"),
        ],
        string="Assign To",
        required=True,
        copy=False,
        default="none",
    )

    assignment_time = fields.Selection(
        [
            ("create_date", "Create Date"),
            ("order_date", "Order Date"),
        ],
        string="Assignment Time",
        required=True,
        default="order_date",
    )

    @api.model
    def _get_base_domain(self, assignment_time, date_from, date_to):
        domain = [("state", "in", ["draft", "sale", "sent", "done"])]

        if assignment_time == "create_date":
            date_field = "create_date"
        else:
            date_field = "date_order"

        if date_from:
            domain = [
                (date_field, ">=", fields.Datetime.from_string(date_from))
            ] + domain
        if date_to:
            domain = [
                (date_field, "<=", fields.Datetime.from_string(date_to))
            ] + domain

        return domain

    def _get_default_order_domain(self):
        # order_domain = []
        return []

    @api.depends("assign_to")
    def _compute_order_domain(self):
        for record in self:
            if not record.assign_to == "condition":
                record.order_domain = ""
            else:
                record.order_domain = repr(record._get_default_order_domain())

    def _parse_order_domain(self):
        self.ensure_one()
        try:
            domain = literal_eval(self.order_domain)
        except Exception:
            domain = [("id", "in", [])]
        return domain

    order_domain = fields.Char(
        string="Orders", compute=_compute_order_domain, readonly=False, store=True
    )

    @api.model_create_multi
    def create(self, values_list):
        last_new_sequence = 0

        for values in values_list:
            if values.get("sequence", None):
                sequence = values["sequence"]
            else:
                sequence = last_new_sequence
                last_new_sequence += 1

            values["sequence"] = sequence

        records = super().create(values_list)

        sequence = last_new_sequence

        for period in self.search(
            [
                ("id", "not in", records.ids),
            ]
        ):
            period.sequence = sequence
            sequence += 1

        return records

    def copy(self, default=None):
        default = dict(default or {})
        default.update(name=_("%s (copy)") % (self.name or ""))
        return super().copy(default)

    def action_recompute_target_sales_periods(self):
        domain = self._get_base_domain(
            self.assignment_time, self.date_from, self.date_to
        ) + self._parse_order_domain()

        self.env["sale.order"].search(domain)._set_default_sales_periods(recompute=True)
