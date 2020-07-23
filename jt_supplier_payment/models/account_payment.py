from odoo import models, fields, api,_
from odoo.exceptions import UserError, ValidationError

class AccountPayment(models.Model):

    _inherit = 'account.payment'

    payment_bank_id = fields.Many2one('res.bank', "Bank of receipt of payment")
    payment_bank_account_id = fields.Many2one('res.partner.bank', "Payment Receipt bank account")
    payment_issuing_bank_acc_id = fields.Many2one('res.partner.bank', "Payment issuing bank Account")
    batch_folio = fields.Integer("Batch Folio")
    folio = fields.Char("Folio against Receipt")
    reason_for_rejection = fields.Text('Reason For Rejection')
    reason_for_cancel = fields.Text('Reason For Cancellation')
    payment_state = fields.Selection([('draft', 'Draft'), 
                              ('for_payment_procedure','For Payment Procedure'),
                               ('posted', 'Validated'), 
                              ('reconciled', 'Reconciled'), 
                              ('rejected','Rejected'),
                              ('cancelled', 'Cancelled')], 
                              readonly=True, default='draft', copy=False, string="Status")
 
    banamex_description = fields.Text('Description',size=24)
    banamex_concept = fields.Text('Concept',size=34)
    banamex_reference = fields.Text('Reference',size=10)
    
    def cancel(self):
        result = super(AccountPayment,self).cancel()
        if self.env.context and self.env.context.get('call_from_reject',False):
            return result
        self.write({'payment_state': 'cancelled'})
        return result
    
    def post(self):
        result = super(AccountPayment,self).post()
        self.write({'payment_state': 'posted'})
        return result
 
    def action_draft(self):
        result = super(AccountPayment,self).action_draft()
        self.write({'payment_state': 'draft'})
        return result
               
    def action_register_payment(self):
        res =super(AccountPayment,self).action_register_payment()
        
        active_ids = self.env.context.get('active_ids')
        if not active_ids:
            return ''
        
        record_ids = self.env['account.move'].browse(active_ids)
        if not record_ids or any(invoice.payment_state != 'approved_payment' and invoice.is_payment_request for invoice in record_ids):
            raise UserError(_("You can only register payment for  Approved for payment request"))
        
#         if not record_ids or any(invoice.state != 'posted' for invoice in record_ids):
#             raise UserError(_("You can only register payments for open invoices"))
        
        record_ids = record_ids.filtered(lambda x:x.is_payment_request and x.is_invoice(include_receipts=True))
        if record_ids:
            amount = self._compute_payment_amount(record_ids, record_ids[0].currency_id, record_ids[0].journal_id,fields.Date.today())
            return {
                'name': _('Schedule Payment'),
                'res_model':'bank.balance.check',
                'view_mode': 'form',
                'view_id': self.env.ref('jt_supplier_payment.view_bank_balance_check').id,
                'context': {'default_total_amount': abs(amount),'default_total_request':len(record_ids),'default_invoice_ids': [(6, 0, record_ids.ids)]},
                'target': 'new',
                'type': 'ir.actions.act_window',
            }
            
        else:
            return res
