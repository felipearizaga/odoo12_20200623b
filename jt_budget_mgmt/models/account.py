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
from odoo import models, fields, api,_
from odoo.exceptions import ValidationError

class AccountMove(models.Model):

    _inherit = 'account.move'

    budget_id = fields.Many2one('expenditure.budget')
    adequacy_id = fields.Many2one('adequacies')
    dependancy_id = fields.Many2one('dependency', string='Dependency')
    sub_dependancy_id = fields.Many2one('sub.dependency', 'Sub Dependency')

    def action_validate_budget(self):
        self.ensure_one()
        str_msg = "Budgetary Insufficiency For Program Code\n\n"
        is_check = False
        budget_msg = "Budget sufficiency"
             
        for line in self.invoice_line_ids:
            if line.program_code_id:
                budget_lines = self.env['expenditure.budget.line'].sudo().search(
                [('program_code_id', '=', line.program_code_id.id),
                 ('expenditure_budget_id', '=', line.program_code_id.budget_id.id),
                 ('expenditure_budget_id.state', '=', 'validate')])
                
                total_available_budget = sum(x.available for x in budget_lines)
                if total_available_budget < line.price_subtotal:
                    is_check = True
                    str_msg += line.program_code_id.program_code+" Available Amount Is "+str(total_available_budget)+"\n\n"
                    

        if is_check:
            return {
                        'name': _('Budgetary Insufficiency'),
                        'type': 'ir.actions.act_window',
                        'res_model': 'budget.insufficien.wiz',
                        'view_mode': 'form',
                        'view_type': 'form',
                        'views': [(False, 'form')],
                        'target': 'new',
                        'context':{'default_msg':str_msg,'default_move_id':self.id,'default_is_budget_suf':False}
                    }
        else:
            return {
                        'name': _('Budget sufficiency'),
                        'type': 'ir.actions.act_window',
                        'res_model': 'budget.insufficien.wiz',
                        'view_mode': 'form',
                        'view_type': 'form',
                        'views': [(False, 'form')],
                        'target': 'new',
                        'context':{'default_msg':budget_msg,'default_move_id':self.id,'default_is_budget_suf':True}
                    }
            
    def action_draft_budget(self):
        self.ensure_one()
        self.payment_state = 'draft'
    
    def action_cancel_budget(self):
        self.ensure_one()
        self.payment_state = 'cancel'

        
class AccountMoveLine(models.Model):

    _inherit = 'account.move.line'

    budget_id = fields.Many2one('expenditure.budget')
    adequacy_id = fields.Many2one('adequacies')
    program_code_id = fields.Many2one('program.code')