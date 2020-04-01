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


class KeyWallet(models.Model):

    _name = 'key.wallet'
    _description = 'Key Wallet'
    _rec_name = 'code'

    code = fields.Char(string='Acronym of the programmatic code')
    description = fields.Text(string='Description of the programmatic code')
    portfolio_key = fields.Integer(string='Portfolio key')
    name_key = fields.Text(string='Name key')
    desc = fields.Text(string='Description')
    entity = fields.Integer(string='Entity')
    project_type = fields.Text(string='Type of program or project')

    _sql_constraints = [('portfolio_key', 'unique(portfolio_key)',
                         'The portfolio key must be unique.')]

    @api.constrains('code')
    def _check_code(self):
        if self.code and not len(self.code) == 2:
            raise ValidationError(_('The code size must be two.'))

    @api.constrains('portfolio_key')
    def _check_portfolio_key(self):
        if self.portfolio_key and not len(str(self.portfolio_key)) == 4:
            raise ValidationError(_('The portfolio key size must be four.'))

    @api.constrains('entity')
    def _check_entity(self):
        if self.entity and not len(str(self.entity)) == 2:
            raise ValidationError(_('The entity size must be two.'))
