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


class CalendarAssignedAmounts(models.Model):

    _name = 'calendar.assigned.amounts'
    _description = 'Calendar of assigned amounts'
    _rec_name = 'date'

    def _get_amount(self):
        for record in self:
            amount_to_receive = 0
            amount_received = 0
            for line in record.line_ids:
                amount_to_receive += line.amount_assigned
                amount_received += line.amount_deposited
            record.amount_to_receive = amount_to_receive
            record.amount_received = amount_received
            record.amount_pending = record.amount_to_receive - record.amount_received

    date = fields.Date(string='Date')
    amount_to_receive = fields.Integer(
        string='Amount to receive', compute='_get_amount')
    amount_received = fields.Integer(
        string='Amount received', compute='_get_amount')
    amount_pending = fields.Integer(
        string='Amount pending', compute='_get_amount')
    observations = fields.Text(string='Comments')
    line_ids = fields.One2many('calendar.assigned.amounts.lines',
                               'calendar_assigned_amount_id', string='Calendar of assigned amount lines')

    @api.model
    def create(self, vals):
        res = super(CalendarAssignedAmounts, self).create(vals)
        vals = {
            'made_by_id': self.env.user.id,
            'calendar_id': res.id,
        }
        control = self.env['control.amounts.received'].create(vals)
        for line in res.line_ids:
            vals = {
                'amount_assigned': line.amount_assigned,
                'deposit_date': line.date,
                'amount_deposited': line.amount_deposited,
                'account_id': line.bank_id.id,
                'observations': line.observations,
                'control_id': control.id,
                'calendar_id': res.id,
            }
            self.env['control.amounts.received.line'].create(vals)
        return res


class CalendarAssignedAmountsLines(models.Model):

    _name = 'calendar.assigned.amounts.lines'
    _description = 'Calendar of assigned amounts lines'
    _rec_name = 'date'

    date = fields.Date(string='Deposit date')
    budget_id = fields.Many2one(
        'budget.program.conversion', string='Budgetary Program')
    month = fields.Char(string='Month of the amount')
    observations = fields.Text(string='Comments')
    amount_assigned = fields.Integer(string='Amount assigned')
    amount_deposited = fields.Integer(string='Amount deposited')
    bank_id = fields.Many2one('res.bank', string='Bank')
    bank_account_id = fields.Many2one(
        'res.partner.bank', string='Bank account')
    calendar_assigned_amount_id = fields.Many2one(
        'calendar.assigned.amounts', string='Calendar of assigned amount')
