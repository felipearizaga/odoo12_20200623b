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
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class DepartureConversion(models.Model):

    _name = 'departure.conversion'
    _description = 'Conversion with Departure'
    _rec_name = 'code'

    code = fields.Char(string='Acronym of the programmatic code')
    description = fields.Text(string='Description of the programmatic code')
    federal_item = fields.Integer(string='Federal item')
    federal_name = fields.Text(string='Federal name')
    # item_id = fields.Many2one('', string='Item')
    # exercise_type_id = fields.Many2one('', string='Execrcise type')
    # item_name_id = fields.Many2one('', string='Item name')

    @api.constrains('code')
    def _check_code(self):
        if self.code and not len(self.code) == 5:
            raise ValidationError(_('The code size must be five.'))

    @api.constrains('federal_item')
    def _check_federal_item(self):
        if self.federal_item and not len(str(self.federal_item)) == 5:
            raise ValidationError(_('The federal item size must be five.'))
