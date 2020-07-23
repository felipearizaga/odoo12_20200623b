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

class GenerateBankLayout(models.TransientModel):

    _name = 'generate.bank.layout'
    _description = 'Generate Bank Layout'
    
    journal_id = fields.Many2one('account.journal','Select the file to generate')
    payment_ids = fields.Many2many('account.payment','account_payment_bank_layout_rel','bank_layout_id','payment_id','Payments')
    file_name = fields.Char('Filename')
    file_data = fields.Binary('Download')

    def action_generate_bank_layout(self):
        active_ids = self.env.context.get('active_ids')
        if not active_ids:
            return ''
        
        return {
            'name': _('Generate Bank Layout'),
            'res_model': 'generate.bank.layout',
            'view_mode': 'form',
            'view_id': self.env.ref('jt_supplier_payment.view_generate_bank_layout').id,
            'context': {'default_payment_ids':[(6,0,active_ids)]},
            'target': 'new',
            'type': 'ir.actions.act_window',
        }    
    def banamex_file_format(self):
        file_data = ''
        file_name = 'banamex.txt'
        
        for payment in self.payment_ids:
            file_data += '03'
            if payment.journal_id.account_type:
                if payment.journal_id.account_type=='check':
                    file_data += '01'
                    if payment.journal_id.branch_number:
                        file_data += payment.journal_id.branch_number.zfill(4)
                    else: 
                        file_data += '0000'                        
                elif payment.journal_id.account_type=='card':
                    file_data += '03'
                    file_data += '0000'
                elif payment.journal_id.account_type=='master':
                    file_data += '06'
                    file_data += '0000'
                else:
                    file_data += '0000'
            if payment.journal_id.bank_account_id:
                file_data += payment.journal_id.bank_account_id.acc_number.zfill(20)
            else:
                temp =''
                file_data +=temp.zfill(20)
            #==== Receipt Bank DATA ===========
            if payment.payment_bank_account_id:
                if payment.journal_id.account_type=='check':
                    file_data += '01'
                    if payment.payment_bank_account_id.branch_number:
                        file_data += payment.payment_bank_account_id.branch_number.zfill(4)
                    else: 
                        file_data += '0000'                        
                elif payment.journal_id.account_type=='card':
                    file_data += '03'
                    file_data += '0000'
                elif payment.journal_id.account_type=='master_acc':
                    file_data += '06'
                    file_data += '0000'
                else:
                    file_data += '00'
                    file_data += '0000'
            if payment.payment_bank_account_id:
                file_data += payment.payment_bank_account_id.acc_number.zfill(20)
            else:
                temp =''
                file_data +=temp.zfill(20)
                
            #====== Amount Data =========
            amount = round(payment.amount, 2)
            amount = str(amount).split('.')
            file_data +=str(amount[0]).zfill(12)
            file_data +=str(amount[1]).zfill(2)
            
            #====== Currency Data =========
            if payment.currency_id:
                if payment.currency_id.name=='USD':
                    file_data +='005'
                elif payment.currency_id.name=='MXN':
                    file_data +='001'
            #====== Description =========
            temp_desc = ''
            if payment.banamex_description:
                temp_desc = payment.banamex_description
            file_data += temp_desc.ljust(24, " ")
    
            #====== banamex_concept =========
            temp_desc = ''
            if payment.banamex_concept:
                temp_desc = payment.banamex_concept
            file_data += temp_desc.ljust(34, " ")
    
            #====== banamex_reference =========
            temp_desc = ''
            if payment.banamex_reference:
                temp_desc = payment.banamex_reference
            file_data += temp_desc.ljust(10, " ")
            
            #====== Currency constant =========
            file_data += "000"
            #====== Current Dat time=========
            currect_time = datetime.today()
            
            file_data +=str(currect_time.day)
            file_data +=str(currect_time.month).zfill(2)
            file_data +=str(currect_time.year)[:2]
            file_data +=str(currect_time.hour)
            file_data +=str(currect_time.minute)
            file_data +="\n"
            
        gentextfile = base64.b64encode(bytes(file_data,'utf-8'))
        self.file_data = gentextfile
        self.file_name = file_name
        
        
    def generate_bank_layout(self):
#        for payment in self.payment_ids:
#             if payment.journal_id.id != self.journal_id.id:
#                 raise UserError(_("The selected layout does NOT match the bank of the selected payments"))
        if self.journal_id.bank_format == 'banamex':
            self.banamex_file_format()
                
        return {
            'name': _('Generate Bank Layout'),
            'res_model': 'generate.bank.layout',
            'res_id' : self.id,
            'view_mode': 'form',
            'target': 'new',
            'type': 'ir.actions.act_window',
        }    
    
    
    
    