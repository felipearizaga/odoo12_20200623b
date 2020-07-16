from odoo import models, fields,_
from odoo.exceptions import UserError, ValidationError

class BalanceCheckWizard(models.TransientModel):
    
    _name = 'balance.check.wizard'
    
    is_balance = fields.Boolean('Is Check',default=False)
    wizard_id = fields.Many2one('bank.balance.check','Wizard')
    
    def accept(self):
        return {
            'name': _('Schedule Payment'),
            'res_model':'bank.balance.check',
            'view_mode': 'form',
            'view_id': self.env.ref('jt_supplier_payment.view_bank_balance_check').id,
            'target': 'new',
            'type': 'ir.actions.act_window',
            'res_id' : self.wizard_id.id,
        }

    def generate_report(self):
        return {
            'name': _('Schedule Payment'),
            'res_model':'bank.balance.check',
            'view_mode': 'form',
            'view_id': self.env.ref('jt_supplier_payment.view_bank_balance_check').id,
            'target': 'new',
            'type': 'ir.actions.act_window',
            'res_id' : self.wizard_id.id,
        }
        