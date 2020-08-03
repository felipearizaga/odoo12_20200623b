from odoo import models, fields, api, _
from odoo.exceptions import UserError
import re

class BankAccountConcept(models.Model):
    _name = 'bank.account.concept'
    
    name = fields.Char('Concept')
    bank_account_id = fields.Many2one('res.partner.bank','Bank Accounts')
