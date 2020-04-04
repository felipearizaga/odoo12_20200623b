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


class Standardization(models.Model):

    _name = 'standardization'
    _description = 'Re-standardization'
    _rec_name = 'folio'

    def _get_count(self):
        for record in self:
            record.record_number = len(record.line_ids)
            record.imported_record_number = len(
                record.line_ids.filtered(lambda l: l.imported == True))

    folio = fields.Integer(string='Folio')
    file = fields.Binary(string='File')
    record_number = fields.Integer(string='Number of records', compute='_get_count')
    imported_record_number = fields.Integer(
        string='Number of imported records', compute='_get_count')
    observations = fields.Text(string='Observations')
    line_ids = fields.One2many(
        'standardization.line', 'standardization_id', string='Standardization lines')

    _sql_constraints = [('folio', 'unique(folio)',
                         'The folio must be unique.')]

    def import_lines(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'import.standardization.line',
            'view_mode': 'form',
            'view_type': 'form',
            'views': [(False, 'form')],
            'target': 'new',
        }


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
