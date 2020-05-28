# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
import magic
import mimetypes
import base64
from odoo import api, models, fields

_logger = logging.getLogger(__name__)


class HrExpense(models.Model):
    _inherit = 'hr.expense'
    
    x_fscan_expense = fields.Char(
        compute='_compute_expense_filename',
    )

    def _compute_expense_filename(self):
        for expense in self:
            if expense.x_scan_expense:
                try:
                    mime = magic.from_buffer(base64.b64decode(expense.with_context(bin_size=False).x_scan_expense), mime=True)
                    mime_ext = mimetypes.guess_extension(mime)
                    if mime_ext == '.jpeg':
                        mime_ext = '.jpg'
                    expense.x_fscan_expense = 'D%s%-2s%s' % (expense.sheet_id.account_move_id.name[-4:] if expense.sheet_id and expense.sheet_id.account_move_id else 'XXXX', expense.id if expense.id else 'XX', mime_ext)
                except Exception as e:
                    _logger.debug('Exception: %s : %s - %s' % (e, expense.id, expense.name))
                    expense.x_fscan_expense = 'ERREUR FICHIER.jpg'
                    pass

    @api.onchange('product_id', 'company_id')
    def _onchange_product_id(self):
        unit_amount = self.unit_amount
        super(HrExpense, self)._onchange_product_id()
        if unit_amount:
            self.unit_amount = unit_amount

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    
    x_fscan_order = fields.Char(
        compute='_compute_scan_filename',
    )
    x_fquadra_pdf = fields.Char(
        compute='_compute_scan_filename',
    )
    x_quadra_pdf = fields.Binary('Scan Facture',
        attachment=True
    )

    def _compute_scan_filename(self):
        for record in self:
            if record.x_scan_order:
                mime = magic.from_buffer(base64.b64decode(record.with_context(bin_size=False).x_scan_order), mime=True)
                mime_ext = mimetypes.guess_extension(mime)
                if mime_ext == '.jpeg':
                    mime_ext = '.jpg'
                record.x_fscan_order = 'AR%s%s' % (record.name[-10:], mime_ext)
            if record.x_quadra_pdf:
                mime = magic.from_buffer(base64.b64decode(record.with_context(bin_size=False).x_quadra_pdf), mime=True)
                mime_ext = mimetypes.guess_extension(mime)
                if mime_ext == '.jpeg':
                    mime_ext = '.jpg'
                record.x_fquadra_pdf = 'Facture%s' % mime_ext

class AccountInvoiceCustom(models.Model):
    _inherit = 'account.invoice'

    invoice_filename = fields.Char(
        compute='_compute_invoice_filename',
    )
    x_fquadra_pdf = fields.Char(
        compute='_compute_invoice_filename',
    )

    def _compute_invoice_filename(self):
        for invoice in self:
            if invoice.x_quadra_pdf:
                mime = magic.from_buffer(base64.b64decode(invoice.with_context(bin_size=False).x_quadra_pdf), mime=True)
                mime_ext = mimetypes.guess_extension(mime)
                if mime_ext == '.jpeg':
                    mime_ext = '.jpg'
                if invoice.number:
                    invoice.x_fquadra_pdf ='%s%s' % (invoice.number[1:].replace('-',''), mime_ext)
                else:
                    invoice.x_fquadra_pdf = 'AXXXXXX%s' % mime_ext
                _logger.debug(mime)
                invoice.invoice_filename = "%s - %s" % (mime, mime_ext)

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    x_fbl_pdf = fields.Char(
        compute='_compute_picking_filename',
    )

    def _compute_picking_filename(self):
        for record in self:
            if record.x_bl_fournisseur_pdf:
                mime = magic.from_buffer(base64.b64decode(record.with_context(bin_size=False).x_bl_fournisseur_pdf), mime=True)
                mime_ext = mimetypes.guess_extension(mime)
                if mime_ext == '.jpeg':
                    mime_ext = '.jpg'
                record.x_fbl_pdf = 'RF_%s%s' % (record.name[-5:], mime_ext)
                
class HRExpenseCreateInvoiceCustom(models.TransientModel):
    _inherit = 'hr.expense.create.invoice'
    
    @api.multi
    def create_invoice(self):
        """Use information from selected invoice to create invoice."""
        self.ensure_one()
        expenses = self.expense_ids.filtered(lambda l: not l.invoice_id)
        if not expenses:
            raise UserError(_('No valid expenses to create invoice'))
        expense = expenses[0]
        _logger.debug(expense)
        invoice_lines = [
            (0, 0, {'product_id': x.product_id.id,
                    'name': x.name,
                    'price_unit': x.unit_amount,
                    'quantity': x.quantity,
                    'account_id': x.account_id.id,
                    'analytic_tag_ids': [(6, 0, x.analytic_tag_ids.ids)],
                    'account_analytic_id': x.analytic_account_id.id,
                    'invoice_line_tax_ids': [(6, 0, x.tax_ids.ids)], })
            for x in expenses
        ]
        invoice_vals = {
            'type': 'in_invoice',
            'reference': expense.name,
            'x_quadra_pdf': expense.x_scan_expense,
            'date_invoice': expense.date,
            'x_quadra_payment_type': 'B',
            'x_analytic_tag_ids': [(6, 0, expense.analytic_tag_ids.ids)],
            'x_account_analytic_id': expense.analytic_account_id.id,
            'invoice_line_ids': invoice_lines, }
        invoice = self.env['account.invoice'].with_context(
            type='purchase').create(invoice_vals)
        self.expense_ids.write({'invoice_id': invoice.id})
        return invoice
