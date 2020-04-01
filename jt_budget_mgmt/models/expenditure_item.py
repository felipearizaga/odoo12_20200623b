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


class ExpenditureItem(models.Model):

    _name = 'expenditure.item'
    _description = 'Item of Expenditure'
    _rec_name = 'name'

    code = fields.Char(string='Acronym of the programmatic code')
    description = fields.Text(string='Description of the programmatic code')
    item = fields.Integer(string='Item')
    exercise_type = fields.Selection([('r', 'R'), ('c', 'C'), ('d', 'D')], string='Type of exercise')
    name = fields.Text(string='Name text')
    # shcp_id = fields.Many2one('', string='Expenditure Item SHCP')
    # desc_id = fields.Many2one('', string='Description of spending item')
    # cog_id = fields.Many2one('', string='COG CONAC')
    # cog_desc_id = fields.Many2one('', string='Description of COG CONAC')
    # account_id = fields.Many2one('', string='Accounting account assigned')

    @api.constrains('code')
    def _check_code(self):
        if self.code and not len(self.code) == 3:
            raise ValidationError(_('The code size must be three.'))

    @api.constrains('item')
    def _check_item(self):
        if self.item and not len(str(self.item)) == 3:
            raise ValidationError(_('The item size must be three.'))
