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
from datetime import datetime

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
    journal_id = fields.Many2one("account.journal", string="Journal")
    state = fields.Selection([('draft', 'Draft'), ('validate', 'Validated')], default='draft')
    move_line_ids = fields.One2many('account.move.line', 'calender_id', string="Journal Items")

    @api.model
    def default_get(self, fields):
        res = super(CalendarAssignedAmounts, self).default_get(fields)
        daily_income_jour = self.env.ref('jt_conac.daily_income_jour')
        if daily_income_jour:
            res.update({'journal_id': daily_income_jour.id})
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
        unam_move_val = {'ref': self.folio, 'calender_id': control_amount.id, 'conac_move': True,
                         'date': today, 'journal_id': journal.id, 'company_id': company_id,
                         'line_ids': [(0, 0, {
                             'account_id': journal.default_credit_account_id.id,
                             'coa_conac_id': journal.conac_credit_account_id.id,
                             'credit': amount, 'calender_id': control_amount.id,
                             'partner_id': partner_id
                         }), (0, 0, {
                             'account_id': journal.default_debit_account_id.id,
                             'coa_conac_id': journal.conac_debit_account_id.id,
                             'debit': amount, 'calender_id': control_amount.id,
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

    @api.model
    def create(self, vals):
        vals['folio'] = self.env['ir.sequence'].next_by_code(
            'control.amount.received') or _('New')
        res = super(CalendarAssignedAmounts, self).create(vals)
        return res

#     @api.constrains('date', 'line_ids')
#     def _check_lines(self):
#         if self.date:
#             date_month = self.date.month
#             months = list(self.line_ids.mapped('month'))
#             month_dict = {
#                 1: 'january',
#                 2: 'february',
#                 3: 'march',
#                 4: 'april',
#                 5: 'may',
#                 6: 'june',
#                 7: 'july',
#                 8: 'august',
#                 9: 'september',
#                 10: 'october',
#                 11: 'november',
#                 12: 'december',
#             }
#             if any(month != month_dict.get(date_month) for month in months):
#                 raise ValidationError("You can only add selected date's month in lines")


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

    currency_id = fields.Many2one(
        'res.currency', default=lambda self: self.env.company.currency_id)
    
    #==== New fields ======#
    year = fields.Char('Year',size=4)
    branch = fields.Integer('Branch')
    unit = fields.Integer('Unit')
    purpose = fields.Integer('Purpose')
    function = fields.Integer('Function')
    sub_function = fields.Integer('Subfunction')
    program = fields.Char('Program')
    institution_activity = fields.Integer('Institution Activity')
    project_identification = fields.Char('Project Identification',size=2)
    project = fields.Char('Project')
    budgetary_program = fields.Char('Budgetary Program')
    item_id = fields.Many2one('departure.conversion','Expense Item')
    expense_type = fields.Integer('Expense Type')
    funding_source = fields.Char('Funding Source')
    federal = fields.Integer('Federal')
    key_wallet = fields.Integer('Key Wallet')
    january = fields.Float(string='January')
    february = fields.Float(string='February')
    march = fields.Float(string='March')
    april = fields.Float(string='April')
    may = fields.Float(string='May')
    june = fields.Float(string='June')
    july = fields.Float(string='July')
    august = fields.Float(string='August')
    september = fields.Float(string='September')
    october = fields.Float(string='October')
    november = fields.Float(string='November')
    december = fields.Float(string='December')
    annual_amount = fields.Float(string='Annual Amount')
    annual_amount_received = fields.Float(string='Annual Amount Received')
    
class AccountMove(models.Model):

    _inherit = 'account.move'

    calender_id = fields.Many2one('calendar.assigned.amounts')

class AccountMoveLine(models.Model):

    _inherit = 'account.move.line'

    calender_id = fields.Many2one('calendar.assigned.amounts')
