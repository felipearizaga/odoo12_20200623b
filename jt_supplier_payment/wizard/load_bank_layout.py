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
from odoo import models, fields,_
from odoo.exceptions import UserError, ValidationError
import base64
from datetime import datetime, timedelta
from odoo.tools.misc import formatLang, format_date, get_lang
from babel.dates import format_datetime, format_date

class loadBankLayoutSupplierPayment(models.TransientModel):

    _name = 'load.bank.layout.supplier.payment'
    _description = 'Load Bank Layout Supplier Payment'
    
    journal_id = fields.Many2one('account.journal','Select the file to generate')
    payment_ids = fields.Many2many('account.payment','account_payment_load_bank_layout_rel','load_bank_layout_id','payment_id','Payments')
    file_name = fields.Char('Filename')
    file_data = fields.Binary('Upload File')
    
    def action_load_bank_layout(self):
        active_ids = self.env.context.get('active_ids')
        for payment in self.env['account.payment'].browse(active_ids):
            if payment.payment_state != 'for_payment_procedure':
                raise UserError(_("You can load Bank Layout only for those payments which are in "
                "'For Payment Procedure'!"))
        if not active_ids:
            return ''
        
        return {
            'name': _('Load Bank Layout'),
            'res_model': 'load.bank.layout.supplier.payment',
            'view_mode': 'form',
            'view_id': self.env.ref('jt_supplier_payment.view_load_bank_layout_supplier_payment_form').id,
            'context': {'default_payment_ids':[(6,0,active_ids)]},
            'target': 'new',
            'type': 'ir.actions.act_window',
        }
    
    def load_bank_layout(self):
        for payment in self.payment_ids:
            if payment.journal_id.id != self.journal_id.id:
                raise UserError(_("The selected layout does NOT match the bank of the selected payments"))
        
