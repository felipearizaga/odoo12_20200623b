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


class Program(models.Model):

    _name = 'program'
    _description = 'Program'
    _rec_name = 'key_unam'

    key_unam = fields.Char(string='Key UNAM', size=2)
    desc_key_unam = fields.Text(string='Description Key UNAM')

    _sql_constraints = [('key_unam', 'unique(key_unam)',
                         'The key UNAM must be unique.')]

    @api.constrains('key_unam')
    def _check_key_unam(self):
        if not str(self.key_unam).isnumeric():
            raise ValidationError(_('The Key UNAM must be numeric value'))
