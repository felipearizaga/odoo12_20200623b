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


class AccountAccount(models.Model):
    _inherit = 'account.account'

    item = fields.Char(string='Item')
    application = fields.Char(string='Applicability')
    flag_coa_conac = fields.Boolean(string="Flag COA CONAC")

    parent_id = fields.Many2one(
        'account.account', string="CONAC Code", domain="[('flag_coa_conac', '=', True)]")
    conac_name = fields.Text(string="Name CONAC")

    @api.onchange('parent_id')
    def _onchange_parent_id(self):
        if self.parent_id:
            self.conac_name = self.parent_id.name
