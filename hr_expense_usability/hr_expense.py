# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models, fields


class HrExpense(models.Model):
    _inherit = 'hr.expense'

    @api.onchange('product_id', 'company_id')
    def _onchange_product_id(self):
        unit_amount = self.unit_amount
        super(HrExpense, self)._onchange_product_id()
        if unit_amount:
            self.unit_amount = unit_amount
