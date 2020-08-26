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
from odoo import models, fields,api,_
from odoo.exceptions import ValidationError
from datetime import datetime

class ControlAmountsReceived(models.Model):

    _name = 'control.amounts.received'
    _description = 'Control of amounts received'
    _rec_name = 'folio'

    def _get_amount(self):
        for record in self:
            record.amount_to_receive = sum(
                record.line_ids.mapped('amount_assigned'))
            record.amount_received = sum(
                record.line_ids.mapped('amount_deposited'))
            record.amount_pending = record.amount_to_receive - record.amount_received

    date = fields.Date(string='Deposit date')
    folio = fields.Integer(string='Folio')
    budget_id = fields.Many2one('expenditure.budget', string='Budget')
    journal_id = fields.Many2one("account.journal", string="Journal")
    file = fields.Binary(string='Seasonal file')
    made_by_id = fields.Many2one('res.users', string='Made by')
    import_date = fields.Date(string='Import date')
    observations = fields.Text(string='Observations')
    line_ids = fields.One2many('control.amounts.received.line',
                               'control_id', string='Control of amounts received lines')
    calendar_assigned_amount_id = fields.Many2one(
        'calendar.assigned.amounts', string='Calendar of assigned amount')
    state = fields.Selection([('draft', 'Draft'), ('validate', 'Validated')], default='draft')

    file = fields.Binary(string='Seasonal File', copy=False)
    filename = fields.Char(string="File Name", copy=False)
    import_date = fields.Date(string='Import Date', copy=False)
    user_id = fields.Many2one('res.users', string='Made By',
                              default=lambda self: self.env.user, tracking=True, copy=False)
    obs_calender_amount = fields.Text(string='Observations')
    obs_cont_amount = fields.Text(string='Observations')
    amount_to_receive = fields.Float(
        string='Amount to receive', compute='_get_amount')
    amount_received = fields.Float(
        string='Amount received', compute='_get_amount')
    amount_pending = fields.Float(
        string='Amount pending', compute='_get_amount')

    total_rows = fields.Integer(string='Total Rows', copy=False)
    diff = fields.Text(string='Difference', copy=False)

    move_line_ids = fields.One2many('account.move.line', 'control_id', string="Journal Items")
        
    @api.depends('date')
    def _compute_month_int(self):
        for record in self:
            record.month_int = 0
            if record.date:
                record.month_int = record.date.month

    month_int = fields.Integer(string='Month Integer', store=True, compute='_compute_month_int')

    @api.model
    def default_get(self, fields):
        res = super(ControlAmountsReceived, self).default_get(fields)
        daily_income_jour = self.env.ref('jt_conac.daily_income_jour')
        if daily_income_jour:
            res.update({'journal_id': daily_income_jour.id})
        return res

    @api.model
    def create(self, vals):
        vals['folio'] = self.env['ir.sequence'].next_by_code(
            'control.amount.received') or _('New')
        res = super(ControlAmountsReceived, self).create(vals)
        return res

    def validate(self):
        self.ensure_one()
        move_obj = self.env['account.move']
        control_amount = self
        journal = control_amount.journal_id
        today = datetime.today().date()
        user = self.env.user
        partner_id = user.partner_id.id
        amount = sum(control_amount.line_ids.mapped('amount_deposited'))
        company_id = user.company_id.id
        if not journal.default_debit_account_id or not journal.default_credit_account_id \
                or not journal.conac_debit_account_id or not journal.conac_credit_account_id:
            raise ValidationError(_("Please configure UNAM and CONAC account in journal!"))
        unam_move_val = {'ref': self.folio, 'control_id': control_amount.id, 'conac_move': True,
                         'date': today, 'journal_id': journal.id, 'company_id': company_id,
                         'line_ids': [(0, 0, {
                             'account_id': journal.default_credit_account_id.id,
                             'coa_conac_id': journal.conac_credit_account_id.id,
                             'credit': amount, 'control_id': control_amount.id,
                             'partner_id': partner_id
                         }), (0, 0, {
                             'account_id': journal.default_debit_account_id.id,
                             'coa_conac_id': journal.conac_debit_account_id.id,
                             'debit': amount, 'control_id': control_amount.id,
                             'partner_id': partner_id
                         })]}
        unam_move = move_obj.create(unam_move_val)
        unam_move.action_post()
        self.state = 'validate'

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

class ControlAmountsReceivedLine(models.Model):

    _name = 'control.amounts.received.line'
    _description = 'Control of amounts received lines'
    _rec_name = 'deposit_date'

    def _get_amount_pending(self):
        for record in self:
            record.amount_pending = record.amount_assigned - record.amount_deposited

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

    bank_id = fields.Many2one('res.bank', string='Bank')
    bank_account_id = fields.Many2one(
        'res.partner.bank', string='Bank account', domain="['|', ('bank_id', '=', False), ('bank_id', '=', bank_id)]")
    
    amount_assigned = fields.Integer(string='Amount assigned')
    deposit_date = fields.Date(string='Deposit date')
    amount_deposited = fields.Integer(string='Amount deposited')
    account_id = fields.Many2one('res.bank', string='Bank')
    amount_pending = fields.Integer(
        string='Amount pending', compute='_get_amount_pending')
    observations = fields.Text(string='Comments')
    control_id = fields.Many2one(
        'control.amounts.received', string='Control of amounts received')
    calendar_assigned_amount_id = fields.Many2one(
        'calendar.assigned.amounts', string='Calendar of assigned amount')


class AccountMove(models.Model):

    _inherit = 'account.move'

    control_id = fields.Many2one('control.amounts.received')

class AccountMoveLine(models.Model):

    _inherit = 'account.move.line'

    control_id = fields.Many2one('control.amounts.received')
