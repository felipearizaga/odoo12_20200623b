# -*- coding: utf-8 -*-
##############################################################################
#
#    Jupical Technologies Pvt. Ltd.
#    Copyright (C) 2018-TODAY Jupical Technologies(<http://www.jupical.com>).
#    Author: Jupical Technologies Pvt. Ltd.(<http://www.jupical.com>)
#    you can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    It is forbidden to publish, distribute, sublicense, or sell copies
#    of the Software or modified copies of the Software.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    GENERAL PUBLIC LICENSE (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from odoo import models, fields, api, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError

class AccountMove(models.Model):

    _inherit = 'account.move'

    @api.model
    def _get_default_journal(self):
        ''' Get the default journal.
        It could either be passed through the context using the 'default_journal_id' key containing its id,
        either be determined by the default type.
        '''
        move_type = self._context.get('default_type', 'entry')
        journal_type = 'general'
        if move_type in self.get_sale_types(include_receipts=True):
            journal_type = 'sale'
        elif move_type in self.get_purchase_types(include_receipts=True):
            journal_type = 'purchase'

        if self._context.get('default_journal_id'):
            journal = self.env['account.journal'].browse(self._context['default_journal_id'])

            if move_type != 'entry' and journal.type != journal_type:
                raise UserError(_("Cannot create an invoice of type %s with a journal having %s as type.") % (
                move_type, journal.type))
        else:
            company_id = self._context.get('force_company',
                                           self._context.get('default_company_id', self.env.company.id))
            domain = [('company_id', '=', company_id), ('type', '=', journal_type)]

            journal = None
            if self._context.get('default_currency_id'):
                currency_domain = domain + [('currency_id', '=', self._context['default_currency_id'])]
                journal = self.env['account.journal'].search(currency_domain, limit=1)

            if not journal:
                journal = self.env['account.journal'].search(domain, limit=1)

            if not journal:
                error_msg = _('Please define an accounting miscellaneous journal in your company')
                if journal_type == 'sale':
                    error_msg = _('Please define an accounting sale journal in your company')
                elif journal_type == 'purchase':
                    error_msg = _('Please define an accounting purchase journal in your company')
                raise UserError(error_msg)

        if 'default_is_payment_request' in self._context:
            journal = self.env.ref('jt_supplier_payment.payment_request_jour')

        return journal
    
    baneficiary_id = fields.Many2one('hr.employee', string="Beneficiary of the payment")
    payment_state = fields.Selection([('draft', 'Draft'),('registered','Registered'),
                                      ('approved_payment','Approved for payment'),
                                      ('for_payment_procedure','For Payment Procedure'),
                                      ('paid','Paid'),
                                      ('payment_not_applied','Payment not Applied'),
                                      ('done','Done'),
                                      ('rejected','Rejected'),
                                      ('cancel','Cancel')],default='draft',copy=False)
    baneficiary_key = fields.Char('Baneficiary Key', related='partner_id.password_beneficiary', store=True)
    rfc = fields.Char("RFC", related='baneficiary_id.rfc', store=True)
    student_account = fields.Char("Student Account")
    transfer_key = fields.Char("Transfer Key")
    category_key = fields.Char("Category Key", related='baneficiary_id.job_id.category_key', store=True)
    workstation_id = fields.Many2one('hr.job', "Appointment", related='baneficiary_id.job_id')
    folio = fields.Char("Folio against Receipt")
    folio_dependency = fields.Char("Folio Dependency")
    operation_type_id = fields.Many2one('operation.type', "Operation Type")
    date_receipt = fields.Datetime("Date of Receipt")
    date_approval_request  = fields.Date("Date Approval Request")
    administrative_forms = fields.Integer("Number of Administrative Forms")
    no_of_document = fields.Integer("Number of Documents")
    sheets = fields.Integer("Sheets")
    payment_method = fields.Selection([('check', 'Check'), ('electronic_transfer', 'Electronic Transfer')])
    document_type = fields.Selection([('national', 'National Currency'), ('foreign', 'Foreign Currency')])
    upa_key = fields.Char('UPA Key')
    upa_document_type = fields.Selection([('01', '01'),
                                          ('02', '02'),
                                          ('03', '03'),
                                          ('04', '04')], string="Document Type UPA")
    batch_folio = fields.Integer("Batch Folio")
    payment_bank_id = fields.Many2one('res.bank', "Bank of receipt of payment")
    payment_bank_account_id = fields.Many2one('res.partner.bank', "Payment Receipt bank account")
    payment_issuing_bank_id = fields.Many2one('account.journal', "Payment issuing Bank")
    payment_issuing_bank_acc_id = fields.Many2one('res.partner.bank', "Payment issuing bank Account")
    responsible_id = fields.Many2one('hr.employee', 'Responsible/Irresponsible')
    administrative_secretary_id = fields.Many2one('hr.employee', 'Administrative Secretary')
    holder_of_dependency_id = fields.Many2one('hr.employee', "Holder of the Dependency")
    invoice_uuid = fields.Char("Invoice UUID")
    invoice_series = fields.Char("Invoice Series")
    folio_invoice = fields.Char("Folio Invoice")
    user_registering_id = fields.Many2one('res.users')
    commitment_date = fields.Date("Commitment Date")
    reason_rejection_req = fields.Text("Reason for Rejecting Request")
    reason_rejection = fields.Text("Reason for Rejection")
    reason_cancellation = fields.Text("Reason for Cancellation")
    is_payment_request = fields.Boolean("Payment Request")
    type = fields.Selection(selection_add=[('payment_req', 'Payment Request')])

    # More info Tab
    reason_for_expendiure = fields.Char("Reason for Expenditure/Trip")
    destination = fields.Char("Destination")
    provenance = fields.Text("Provenance")
    zone = fields.Integer("Zone")
    rate = fields.Monetary("Rate")
    days = fields.Integer("Days")
    responsible_expend_id = fields.Many2one('hr.employee', "Name of the responsible")
    rf_person = fields.Char("RFC of the person in charge")
    responsible_category_key = fields.Char("Responsible category key")
    manager_job_id = fields.Many2one('hr.job', "Manager’s job")
    payment_line_ids = fields.One2many('account.move.line', 'payment_req_id')
    journal_id = fields.Many2one('account.journal', string='Journal', required=True, readonly=True,
        states={'draft': [('readonly', False)]},
        domain="[('company_id', '=', company_id)]",
        default=_get_default_journal)

#     @api.onchange('baneficiary_id')
#     def onchange_baneficiary(self):
#         if self.baneficiary_id and not self.baneficiary_id.address_id:
#             raise ValidationError("Please configure partner into baneficiary")
#         elif self.baneficiary_id:
#             self.partner_id = self.baneficiary_id.address_id.id
        
    def _get_move_display_name(self, show_ref=False):
        ''' Helper to get the display name of an invoice depending of its type.
        :param show_ref:    A flag indicating of the display name must include or not the journal entry reference.
        :return:            A string representing the invoice.
        '''
        self.ensure_one()
        draft_name = ''
        if self.state == 'draft':
            draft_name += {
                'out_invoice': _('Draft Invoice'),
                'out_refund': _('Draft Credit Note'),
                'in_invoice': _('Draft Bill'),
                'in_refund': _('Draft Vendor Credit Note'),
                'out_receipt': _('Draft Sales Receipt'),
                'in_receipt': _('Draft Purchase Receipt'),
                'entry': _('Draft Entry'),
            }[self.type]
            if not self.name or self.name == '/':
                draft_name += ' (* %s)' % str(self.id)
            else:
                draft_name += ' ' + self.name
        return (draft_name or self.name) + (show_ref and self.ref and ' (%s%s)' % (self.ref[:50], '...' if len(self.ref) > 50 else '') or '')

    def action_register(self):
        for move in self:
            move.payment_state = 'registered'

    def check_operation_name(self):
        if self.operation_type_id and self.operation_type_id.name:
            my_str = "Payment to supplier"
            if self.operation_type_id.name.upper() == my_str.upper():
                return True
        return False

#     def remove_journal_line(self):
#         if self.

#     @api.onchange('invoice_line_ids')
#     def _onchange_invoice_line_ids(self):
#         res = super(AccountMove,self)._onchange_invoice_line_ids()
#         if self.is_payment_request:
#             #{'subtype_ids': [(3, sid) for sid in old_sids]}
#             #self.line_ids = [(3, sid) for sid in self.line_ids.ids]
#             self.line_ids = [(5,self.line_ids.ids)]
#         return res
            
class AccountMoveLine(models.Model):

    _inherit = 'account.move.line'

    payment_req_id = fields.Many2one('account.move')
    egress_key_id = fields.Many2one("egress.keys", "Egress Key")
    type_of_bussiness_line = fields.Char("Type Of Bussiness Line")
    other_amounts = fields.Monetary("Other Amounts")
    amount = fields.Monetary("Amount")
    price_payment = fields.Monetary("Price")
    sub_total_payment = fields.Monetary("Sub Total")
    tax = fields.Float("Tax")

