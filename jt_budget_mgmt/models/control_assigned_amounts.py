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
from odoo.exceptions import ValidationError
from odoo import models, fields, api, _


class ControlAssignedAmounts(models.Model):

    _name = 'control.assigned.amounts'
    _description = 'Control of Assigned Amounts'
    _rec_name = 'folio'

    folio = fields.Char(string='Folio')
    import_file = fields.Binary(string='File to import')
    budget_id = fields.Many2one('expenditure.budget', string='Budget')
    user_id = fields.Many2one('res.users', string='Made by', default=lambda self: self.env.user, tracking=True)
    import_date = fields.Date(string='Import date')
    observations = fields.Text(string='Observations')
    state = fields.Selection([('draft', 'Draft'), ('process', 'In process'),
                              ('validated', 'Validated'),
                              ('rejected', 'Rejected'),
                              ('canceled', 'Canceled')], default='draft', required=True, string='Status')
    line_ids = fields.One2many('control.assigned.amounts.lines',
                               'assigned_amount_id', string='Assigned amount lines')

    _sql_constraints = [
        ('folio', 'unique(folio)', 'The folio must be unique.')]

    @api.constrains('folio')
    def _check_folio(self):
        if not str(self.folio).isnumeric():
            raise ValidationError('Folio Must be numeric value!')

    def import_lines(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'import.assigned.amount.line',
            'view_mode': 'form',
            'view_type': 'form',
            'views': [(False, 'form')],
            'target': 'new',
        }

    def confirm(self):
        self.state = 'process'

    def validate(self):
        self.state = 'validated'

    def reject(self):
        self.state = 'rejected'

    def cancel(self):
        self.state = 'canceled'


class ControlAssignedAmountsLines(models.Model):

    _name = 'control.assigned.amounts.lines'
    _description = 'Control Assigned Amounts Lines'
    _rec_name = 'code'

    code = fields.Many2one('program.code', string='Code program')
    start_date = fields.Date(string='Start date')
    end_date = fields.Date(string='End date')
    authorized = fields.Integer(string='Authorized')
    assigned = fields.Integer(string='Assigned')
    available = fields.Integer(string='Available')
    assigned_amount_id = fields.Many2one(
        'control.assigned.amounts', string='Assigned amount')

    _sql_constraints = [
        ('unique_assigned_amount_id_program_code', 'unique(code,assigned_amount_id)', 'The program code must be unique per Control of Assigned Amounts')]
