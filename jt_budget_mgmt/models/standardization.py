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
from odoo import models, fields, _
from odoo.exceptions import UserError


class Standardization(models.Model):

    _name = 'standardization'
    _description = 'Re-standardization'
    _rec_name = 'folio'

    def _get_count(self):
        for record in self:
            record.record_number = len(record.line_ids)
            record.imported_record_number = len(
                record.line_ids.filtered(lambda l: l.imported == True))
            record.draft_count = len(
                record.line_ids.filtered(lambda l: l.state == 'draft'))
            record.received_count = len(
                record.line_ids.filtered(lambda l: l.state == 'received'))
            record.in_process_count = len(
                record.line_ids.filtered(lambda l: l.state == 'in_process'))
            record.authorized_count = len(
                record.line_ids.filtered(lambda l: l.state == 'authorized'))
            record.cancelled_count = len(
                record.line_ids.filtered(lambda l: l.state == 'cancelled'))

    folio = fields.Integer(string='Folio', states={'draft': [('readonly', False)]})
    file = fields.Binary(string='File', states={'draft': [('readonly', False)]})
    record_number = fields.Integer(
        string='Number of records', compute='_get_count')
    imported_record_number = fields.Integer(
        string='Number of imported records', compute='_get_count')
    observations = fields.Text(string='Observations', states={'draft': [('readonly', False)]})
    line_ids = fields.One2many(
        'standardization.line', 'standardization_id', string='Standardization lines', states={'draft': [('readonly', False)]})
    state = fields.Selection([('draft', 'Draft'), ('confirmed', 'Confirmed'),
                              ('cancelled', 'Cancelled')], default='draft', required=True, string='State')
    draft_count = fields.Integer(string='Draft', compute='_get_count')
    received_count = fields.Integer(string='Received', compute='_get_count')
    in_process_count = fields.Integer(
        string='In process', compute='_get_count')
    authorized_count = fields.Integer(
        string='Authorized', compute='_get_count')
    cancelled_count = fields.Integer(string='Cancelled', compute='_get_count')

    _sql_constraints = [('folio', 'unique(folio)',
                         'The folio must be unique.')]

    def confirm(self):
        for line in self.line_ids:
            if line.amount < 5000:
                raise UserError(_('Please enter amount greater than or equal to 5000.'))
        self.state = 'confirmed'

    def cancel(self):
        self.state = 'cancelled'

    def import_lines(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'import.standardization.line',
            'view_mode': 'form',
            'view_type': 'form',
            'views': [(False, 'form')],
            'target': 'new',
        }

    def action_draft(self):
        lines = self.line_ids.filtered(lambda l: l.selected == True)
        for line in lines:
            line.state = 'draft'

    def action_received(self):
        lines = self.line_ids.filtered(
            lambda l: l.selected == True and l.state == 'draft')
        for line in lines:
            line.state = 'received'

    def action_in_process(self):
        lines = self.line_ids.filtered(
            lambda l: l.selected == True and l.state == 'received')
        for line in lines:
            line.state = 'in_process'

    def action_authorized(self):
        lines = self.line_ids.filtered(
            lambda l: l.selected == True and l.state == 'in_process')
        for line in lines:
            line.state = 'authorized'

    def action_cancelled(self):
        lines = self.line_ids.filtered(lambda l: l.selected == True)
        for line in lines:
            line.state = 'cancelled'
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'reject.standardization.line',
            'view_mode': 'form',
            'view_type': 'form',
            'views': [(False, 'form')],
            'target': 'new',
            'context': {'parent_id': self.id, }
        }

    def draft_button(self):
        action = self.env.ref(
            'jt_budget_mgmt.action_standardization_lines').read()[0]
        action['view_mode'] = 'tree'
        action['domain'] = [
            ('standardization_id', '=', self.id), ('state', '=', 'draft')]
        return action

    def received_button(self):
        action = self.env.ref(
            'jt_budget_mgmt.action_standardization_lines').read()[0]
        action['view_mode'] = 'tree'
        action['domain'] = [
            ('standardization_id', '=', self.id), ('state', '=', 'received')]
        return action

    def in_process_button(self):
        action = self.env.ref(
            'jt_budget_mgmt.action_standardization_lines').read()[0]
        action['view_mode'] = 'tree'
        action['domain'] = [
            ('standardization_id', '=', self.id), ('state', '=', 'in_process')]
        return action

    def authorized_button(self):
        action = self.env.ref(
            'jt_budget_mgmt.action_standardization_lines').read()[0]
        action['view_mode'] = 'tree'
        action['domain'] = [
            ('standardization_id', '=', self.id), ('state', '=', 'authorized')]
        return action

    def cancelled_button(self):
        action = self.env.ref(
            'jt_budget_mgmt.action_standardization_lines').read()[0]
        action['view_mode'] = 'tree'
        action['domain'] = [
            ('standardization_id', '=', self.id), ('state', '=', 'cancelled')]
        return action


class StandardizationLine(models.Model):

    _name = 'standardization.line'
    _description = 'Re-standardization Lines'
    _rec_name = 'folio'

    folio = fields.Integer(string='Folio')
    code_id = fields.Many2one('program.code', string='Code')
    budget_id = fields.Many2one('expenditure.budget', string='Budget')
    amount = fields.Monetary(string='Amount', currency_field='currency_id')
    origin_id = fields.Many2one('resource.origin', string='Origin')
    quarter = fields.Text(string='Quarter')
    stage_id = fields.Many2one('stage', string='Stage')
    reason = fields.Text(string='Reason for rejection')
    standardization_id = fields.Many2one(
        'standardization', string='Standardization')
    currency_id = fields.Many2one(
        'res.currency', default=lambda self: self.env.user.company_id.currency_id)
    imported = fields.Boolean(default=False)
    selected = fields.Boolean(default=False)
    state = fields.Selection([('draft', 'Draft'), ('received', 'Received'),
                              ('in_process', 'In process'),
                              ('authorized', 'Authorized'),
                              ('cancelled', 'Cancelled')], default='draft',
                             required=True, string='State')
