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

class PaymentRequest(models.Model):

    _name = 'payment.request'
    _description = "Payment Request"

    baneficiary_id = fields.Many2one('hr.employee')
    partner_id = fields.Many2one("res.partner")
    baneficiary_key = fields.Char('Baneficiary Key', related='partner_id.password_beneficiary', store=True)
    rfc = fields.Char("RFC", related='partner_id.rfc', store=True)
    student_account = fields.Char("Student Account")
    transfer_key = fields.Char("Transfer Key")
    category_key = fields.Char("Category Key", related='baneficiary_id.job_id.category_key', store=True)
    workstation_id = fields.Many2one('hr.job', "Work Station", related='baneficiary_id.job_id')
    folio = fields.Char("Folio against Receipt")
    folio_dependency = fields.Char("Folio Dependency")
    operation_type = fields.Many2one('operation.type', "Operation Type")
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
    payment_issuing_bank_id = fields.Many2one('account.journal', "Payment issuing Bank")
    payment_bank_account_id = fields.Many2one('res,partner.bank', "Payment Receipt bank account")
    payment_issuing_bank_acc_id = fields.Many2one('res.partner.bank', "Payment issuing bank Account")
    responsible_id = fields.Many2one('hr.employee', 'Responsible/Irresponsible')
    administrative_secretary_id = fields.Many2one('Administrative Secretary')
    holder_of_dependency_id = fields.Many2one("Holder of the Dependency")
    invoice_uuid = fields.Char("Invoice UUID")
    invoice_series = fields.Char("Invoice Series")
    folio_invoice = fields.Char("Folio Invoice")
    user_registering = fields.Many2one('res.users')
    commitment_date = fields.Date("Commitment Date")
    payment_req_journal_id = fields.Many2one('account.journal', "Journal")
    reason_rejection = fields.Text("Reason for Rejection")
    invoice_date = fields.Date("Invoice Date")
    currency_id = fields.Many2one('res.currency')

    # More info Tab
    reason_for_expendiure = fields.Text("Reason for Expenditure/Trip")
    destination = fields.Text("Destination")
    provenance = fields.Text("Provenance")
    zone = fields.Integer("Zone")
    rate = fields.Monetary("Rate")
    days = fields.Integer("Days")
    responsible_expend_id = fields.Many2one('hr.employee', "Name of the responsible")
    rf_person = fields.Char("RFC of the person in charge")
    responsible_category_key = fields.Char("Responsible category key")
    manager_job_id = fields.Many2one('hr.job', "Manager’s job")

class PaymentRequestLine(models.Model):

    _name = 'payment.request.line'
    _description = "Payment Request Line"

    product_id = fields.Many2one('product.product', "Product")
    description = fields.Text("Description")
    account_id = fields.Many2one("Account")
    egress_key_id = fields.Many2one("egress.keys", "Egress Key")
    type_of_bussiness_line = fields.Char("Type Of Bussiness Line")
    other_amounts = fields.Monetary("Other Amounts")
    amount = fields.Monetary("Amount")
    price = fields.Monetary("Price")
    sub_total = fields.Monetary("Sub Total")
    tax = fields.Float("Tax")
    currency_id = fields.Many2one('res.currency')