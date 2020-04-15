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
    _rec_name = 'key_origin'

    key_origin = fields.Selection([
        ('0', '00'),
        ('1', '01'),
        ('2', '02'),
        ('3', '03'),
        ('4', '04'),
        ('5', '05')], string='Key origin of the resource')
    desc = fields.Selection([
        ('subsidy', 'Federal Subsidy'),
        ('income', 'Extraordinary Income'),
        ('service', 'Education Services'),
        ('financial', 'Financial'),
        ('other', 'Other Products'),
        ('pef', 'Returns Reassignment PEF')],
        string='Description of origin of the resource')

    _sql_constraints = [('key_origin', 'unique(key_origin)', 'The key origin must be unique.')]

    @api.constrains('key_origin', 'desc')
    def _check_field_relation(self):
        flag = False
        if self.key_origin == '0' and self.desc != 'subsidy':
            flag = True
        elif self.key_origin == '1' and self.desc != 'income':
            flag = True
        elif self.key_origin == '2' and self.desc != 'service':
            flag = True
        elif self.key_origin == '3' and self.desc != 'financial':
            flag = True
        elif self.key_origin == '4' and self.desc != 'other':
            flag = True
        elif self.key_origin == '5' and self.desc != 'pef':
            flag = True
        if flag:
            raise ValidationError(_('Please select correct key Origin of the resource!'))
