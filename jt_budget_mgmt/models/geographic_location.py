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


class GeographicLocation(models.Model):

    _name = 'geographic.location'
    _description = 'Geographic Location'
    _rec_name = 'code'

    code = fields.Char(string='Abbreviation of the program code')
    description = fields.Text(string='Description of the program code')
    state_key = fields.Integer(string='State key')
    state_name = fields.Text(string='State name')

    _sql_constraints = [('state_key', 'unique(state_key)',
                         'The state key must be unique.')]

    @api.constrains('code')
    def _check_code(self):
        if self.code and not len(self.code) == 2:
            raise ValidationError(_('The code size must be two.'))

    @api.constrains('state_key')
    def _check_state_key(self):
        if self.state_key and not len(str(self.state_key)) == 2:
            raise ValidationError(_('The state key size must be two.'))
