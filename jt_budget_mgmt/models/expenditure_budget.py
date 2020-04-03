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
from odoo import models, fields, api


class ExpenditureBudget(models.Model):

    _name = 'expenditure.budget'
    _description = 'Expenditure Budget'
    _rec_name = 'budget_name'

    budget_name = fields.Text(string='Budget name')
    responsible_id = fields.Many2one('res.users', string='Responsible')
    from_date = fields.Date(string='Period')
    to_date = fields.Date()
    total_budget = fields.Float(string='Total budget')
    record_number = fields.Integer(string='Number of records')
    import_record_number = fields.Integer(
        string='Number of imported records', readonly=True)
    line_ids = fields.One2many(
        'expenditure.budget.line', 'expenditure_budget_id',
        string='Expenditure Budget Lines')
    state = fields.Selection([('draft', 'Draft'), ('previous', 'Previous'),
                              ('confirm', 'Confirm'), ('validate', 'Validate'),
                              ('done', 'Done')], default='draft', required=True, string='State')

    @api.onchange('line_ids')
    def import_record_count(self):
        if self.line_ids:
            self.import_record_number = len(self.line_ids)
        else:
            self.import_record_number = 0

    def import_lines(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'import.line',
            'view_mode': 'form',
            'view_type': 'form',
            'views': [(False, 'form')],
            'target': 'new',
        }

    def confirm(self):
        self.state = 'confirm'

    def approve(self):
        self.state = 'validate'

    def reject(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'reject',
            'view_mode': 'form',
            'view_type': 'form',
            'views': [(False, 'form')],
            'target': 'new',
        }


class ExpenditureBudgetLine(models.Model):

    _name = 'expenditure.budget.line'
    _description = 'Expenditure Budget Line'
    _rec_name = 'code'

    code = fields.Char(string='Program code')
    start_date = fields.Date(string='Start date')
    end_date = fields.Date(string='End date')
    approved = fields.Monetary(string='Approved', currency_field='currency_id')
    allocated = fields.Monetary(
        string='Allocated', currency_field='currency_id')
    # available = fields.(string='Available')
    expenditure_budget_id = fields.Many2one(
        'expenditure.budget', string='Expenditure Budget')
    currency_id = fields.Many2one(
        'res.currency', default=lambda self: self.env.user.company_id.currency_id)
