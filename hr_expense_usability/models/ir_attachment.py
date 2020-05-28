# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models, fields


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    @api.multi
    def action_set_default_expense_scan(self):
        Expense = self.env['hr.expense']
        for record in self:
            if record.res_model == 'hr.expense':
                expense = Expense.browse([record.res_id])
                expense.write({
                    'x_scan_expense': record.datas,
                    'x_scan_mime': record.name[-3:]
                })
                return {
                    'type': 'ir.actions.act_window',
                    'name': 'Note de frais',
                    'target': 'current',
                    'res_model': record.res_model,
                    'res_id': record.res_id,
                    'view_type': 'form',
                    'views': [[False,'form']],
            	}
