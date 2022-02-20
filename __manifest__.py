# Copyright 2022 <mj@ayudoo.bg>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).

{
    "author": "Michael Jurke, Ayudoo EOOD",
    "name": "Sale Reporting Periods",
    "version": "0.1",
    "summary": "Report Helper for you custom Sales Periods",
    "description": """
        Filter and organize your quotations and sale orders by sales periods, with
        start and end date, as well as complex conditions.
    """,
    "license": "LGPL-3",
    "category": "Sales/Sales",
    "support": "support@ayudoo.bg",
    "depends": [
        "base",
        "sale_management",
    ],
    "data": [
        "security/ir.model.access.csv",
        "report/sale_report_view.xml",
        "views/sale_order_view.xml",
        "views/sales_period_view.xml",
        "views/res_config_settings_view.xml",
    ],
    "application": True,
    "installable": True,
    "demo": [],
}
