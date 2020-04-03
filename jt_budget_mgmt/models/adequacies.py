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
from odoo import models, fields


class Adequacies(models.Model):

    _name = 'adequacies'
    _description = 'Adequacies'
    _rec_name = 'folio'

    folio = fields.Integer(string='Folio')
    budget_id = fields.Many2one('expenditure.budget', string='Budget')
    from_date = fields.Date(string='Observations')
    to_date = fields.Date()
    reason = fields.Text(string='Reason for rejection')
    record_number = fields.Integer(string='Number of records')
    imported_record_number = fields.Integer(
        string='Number of records imported.')
    state = fields.Selection(
        [('draft', 'Draft'), ('confirmed', 'Confirmed'),
         ('accepted', 'Accepted'), ('rejected', 'Rejected')],
        default='draft', required=True, string='State')
    adequacies_lines_ids = fields.One2many(
        'adequacies.lines', 'adequacies_id', string='Adequacies Lines')

    _sql_constraints = [
        ('folio', 'unique(folio)', 'The folio must be unique.')]

    def confirm(self):
        self.state = 'confirmed'

    def accept(self):
        self.state = 'accepted'

    def reject(self):
        self.state = 'rejected'


class AdequaciesLines(models.Model):

    _name = 'adequacies.lines'
    _description = 'Adequacies Lines'
    _rec_name = ''

    program = fields.Char(string='Program')
    line_type = fields.Selection(
        [('increase', 'Increase'), ('decrease', 'Decrease')], string='Type')
    amount = fields.Date(string='Date')
    creation_type = fields.Selection(
        [('manual', 'Manual'), ('imported', 'Imported')],
        string='Creation type')
    adequacies_id = fields.Many2one('adequacies', string='Adequacies')
