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


class COACONAC(models.Model):
    _name = 'coa.conac'
    _description = 'COA CONAC'
    _rec_name = 'display_name'

    code = fields.Char(string='Code')
    name = fields.Char(string='CONAC Name')
    gender = fields.Char(string='Gender')
    group = fields.Char(string='Group')
    item = fields.Char(string='Item')
    applicability = fields.Selection([
        ('debtor', 'Debtor'),
        ('creditor', 'Creditor'),
        ('debtor_creditor', 'Debtor / Creditor')], string='Applicability')
    parent_id = fields.Many2one('coa.conac', string='Parent')

    def _compute_display_name(self):
        for account in self:
            account.display_name = str(account.code) + ' ' + str(account.name)

    display_name = fields.Char(string='Account Name', compute="_compute_display_name")
