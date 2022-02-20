from odoo import models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    def action_recompute_sales_periods(self):
        self.env["sale.order"].search([])._set_default_sales_periods(recompute=True)
