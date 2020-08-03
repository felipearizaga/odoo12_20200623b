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
from odoo.exceptions import UserError
import re

class AccountJournal(models.Model):
    _inherit = 'account.journal'

    account_type = fields.Selection([('check', 'Checks'), ('card', 'Card'),
                                     ('master', 'Master Account'),
                                     ('key', 'Key Account')],
                                    string='Type of Account')
    branch_number = fields.Char('Branch Number', size=4)

    #Bank Accounts
    customer_number = fields.Char('Customer number')
    branch_office = fields.Char('Branch office')
    unam_account_name = fields.Char("UNAM Account Name")
    contract_number = fields.Char('Contract number')
    opening_date = fields.Date('Opening date')
    cancellation_date = fields.Date('Cancellation date')
    concept_id = fields.Many2one('bank.account.concept',string='Concept')
    has_checkbook = fields.Boolean(
        default=False, string='Do you have a checkbook?')
    checkbook_type = fields.Selection(
        [('normal', 'Normal'), ('massive', 'Massive')], string='Type of checkbook')
    signatures = fields.Binary('Account Authorization Signatures')
    contract = fields.Binary('Attach contract')
    min_balance = fields.Monetary(string='Minimum Balance', tracking=True)
    executive_ids = fields.One2many('executive.data', 'journal_id')
    clabe_account = fields.Char(related='bank_account_id.l10n_mx_edi_clabe',string='CLABE Account')

    @api.constrains('min_balance')
    def check_min_balance(self):
        if self.min_balance and self.min_balance < 0:
            raise UserError(_('The balance cannot be negative.'))

    @api.constrains('branch_number')
    def check_branch_number(self):
        if self.branch_number:
            pattern = "^[0-9]{4}$"
            if not re.match(pattern, self.branch_number):
                raise UserError(_('The Branch Number should be of 4 digits.'))
        if self.branch_number and len(self.branch_number) != 4:
            raise UserError(_('The Branch Number should be of 4 digits.'))

class ExecutiveData(models.Model):

    _name = 'executive.data'
    _description = "Executive Data"

    journal_id = fields.Many2one('account.journal')
    name = fields.Char('Name')
    position = fields.Char('Position')
    telephone = fields.Char('Telephone')
    address = fields.Char('Address')
    email = fields.Char('Email')