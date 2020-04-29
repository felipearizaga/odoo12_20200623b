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


class CalendarAssignedAmounts(models.Model):

    _name = 'calendar.assigned.amounts'
    _description = 'Calendar of assigned amounts'
    _rec_name = 'date'

    def _get_amount(self):
        for record in self:
            record.amount_to_receive = sum(
                record.line_ids.mapped('amount_assigned'))
            record.amount_received = sum(
                record.line_ids.mapped('amount_deposited'))
            record.amount_pending = record.amount_to_receive - record.amount_received

    # Fields for control of amount received
    folio = fields.Char(string='Folio')
    budget_id = fields.Many2one('expenditure.budget', domain=[
                                ('state', '=', 'validate')])
    user_id = fields.Many2one('res.users', string='Made By',
                              default=lambda self: self.env.user, tracking=True, copy=False)
    file = fields.Binary(string='Seasonal File', copy=False)
    filename = fields.Char(string="File Name", copy=False)
    import_date = fields.Date(string='Import Date', copy=False)
    obs_cont_amount = fields.Text(string='Observations')
    total_rows = fields.Integer(string='Total Rows', copy=False)
    diff = fields.Text(string='Difference', copy=False)

    # Fields for Calender of assigned amounts
    date = fields.Date(string='Date')
    amount_to_receive = fields.Float(
        string='Amount to receive', compute='_get_amount')
    amount_received = fields.Float(
        string='Amount received', compute='_get_amount')
    amount_pending = fields.Float(
        string='Amount pending', compute='_get_amount')
    obs_calender_amount = fields.Text(string='Observations')

    @api.depends('date')
    def _compute_month_int(self):
        for record in self:
            record.month_int = 0
            if record.date:
                record.month_int = record.date.month

    month_int = fields.Integer(string='Month Integer', store=True, compute='_compute_month_int')

    line_ids = fields.One2many('calendar.assigned.amounts.lines',
                               'calendar_assigned_amount_id', string='Calendar of assigned amount lines')

    def import_lines(self):
        return {
            'name': "Import and Validate File",
            'type': 'ir.actions.act_window',
            'res_model': 'import.control.amount.lines',
            'view_mode': 'form',
            'view_type': 'form',
            'views': [(False, 'form')],
            'target': 'new',
        }

    @api.model
    def create(self, vals):
        vals['folio'] = self.env['ir.sequence'].next_by_code(
            'control.amount.received') or _('New')
        res = super(CalendarAssignedAmounts, self).create(vals)
        return res

    @api.constrains('date', 'line_ids')
    def _check_lines(self):
        if self.date:
            date_month = self.date.month
            months = list(self.line_ids.mapped('month'))
            month_dict = {
                1: 'january',
                2: 'february',
                3: 'march',
                4: 'april',
                5: 'may',
                6: 'june',
                7: 'july',
                8: 'august',
                9: 'september',
                10: 'october',
                11: 'november',
                12: 'december',
            }
            if any(month != month_dict.get(date_month) for month in months):
                raise ValidationError("You can only add selected date's month in lines")


class CalendarAssignedAmountsLines(models.Model):

    _name = 'calendar.assigned.amounts.lines'
    _description = 'Calendar of assigned amounts lines'
    _rec_name = 'date'

    date = fields.Date(string='Deposit date')
    shcp_id = fields.Many2one(
        'shcp.code', string='Budgetary Program')
    month = fields.Selection([
        ('january', 'January'),
        ('february', 'February'),
        ('march', 'March'),
        ('april', 'April'),
        ('may', 'May'),
        ('june', 'June'),
        ('july', 'July'),
        ('august', 'August'),
        ('september', 'September'),
        ('october', 'October'),
        ('november', 'November'),
        ('december', 'December')], string='Month of the amount', default='january')
    amount_assigned = fields.Float(string='Amount assigned')
    amount_deposited = fields.Float(string='Amount deposited')

    def _compute_amount_pending(self):
        for line in self:
            line.amount_pending = line.amount_assigned - line.amount_deposited

    amount_pending = fields.Float(
        string='Amount Pending', compute="_compute_amount_pending")
    bank_id = fields.Many2one('res.bank', string='Bank')
    bank_account_id = fields.Many2one(
        'res.partner.bank', string='Bank account', domain="['|', ('bank_id', '=', False), ('bank_id', '=', bank_id)]")
    observations = fields.Text(string='Observations')
    calendar_assigned_amount_id = fields.Many2one(
        'calendar.assigned.amounts', string='Calendar of assigned amount')
