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


class ResourceOrigin(models.Model):

    _name = 'resource.origin'
    _description = 'Origin of the Resource'
    _rec_name = 'name'

    code = fields.Char(string='Acronym of the programmatic code')
    description = fields.Text(string='Description of the programmatic code')
    key_revenue = fields.Selection(
        [('00', '00'), ('01', '01'), ('02', '02'), ('03', '03'), ('04', '04'),
         ('05', '05')], string='Key own revenue')
    own_revenue = fields.Selection([('subsidy', 'Federal Subsidy'),
                                    ('income', 'Extraordinary Income'),
                                    ('service', 'Education Servicess'),
                                    ('financial', 'Financial'),
                                    ('other', 'Other Products'),
                                    ('pef', 'Returns Reassignment PEF')],
                                   string='Own revenue')
    name = fields.Text(string='Name')

    @api.constrains('code')
    def _check_code(self):
        if self.code and not len(self.code) == 2:
            raise ValidationError(_('The code size must be two.'))
