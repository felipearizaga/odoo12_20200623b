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
                if payment.payment_bank_account_id.account_type=='check':
                    file_data += '01'
                    if payment.payment_bank_account_id.branch_number:
                        file_data += payment.payment_bank_account_id.branch_number.zfill(4)
                    else: 
                        file_data += '0000'                        
                elif payment.payment_bank_account_id.account_type=='card':
                    file_data += '03'
                    file_data += '0000'
                elif payment.payment_bank_account_id.account_type=='master_acc':
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
        
    def bbva_tnn_ptc_file_format(self):
        file_data = ''
        file_name = 'BBVA BANCOMER NET CASH​ (TNN or PTC).txt'
        
        for payment in self.payment_ids:
            #==== Receipt Bank DATA ===========#            
            if payment.payment_bank_account_id:
                file_data += payment.payment_bank_account_id.acc_number.zfill(18)
            else:
                temp =''
                file_data +=temp.zfill(18)
            #======= Bank Issuance of payment ======#    
            if payment.journal_id.bank_account_id:
                file_data += payment.journal_id.bank_account_id.acc_number.zfill(18)
            else:
                temp =''
                file_data +=temp.zfill(18)
            #====== Currency Data =========#
            if payment.currency_id:
                if payment.currency_id.name=='USD':
                    file_data +='USD'
                elif payment.currency_id.name=='MXN':
                    file_data += 'MXP'
                else:
                    file_data += payment.currency_id.name
            #====== Amount Data =========#
            amount = round(payment.amount, 2)
            amount = str(amount).split('.')
            file_data +=str(amount[0]).zfill(13)
            file_data +='.'
            file_data +=str(amount[1]).zfill(2)
            
            #=====reason for payment======#
            reason_payment = 'PAGO'
            if payment.payment_date:
                payment_year = str(payment.payment_date.year)[:2]
                month_name = format_datetime(payment.payment_date, 'MMMM', locale=get_lang(self.env).code)
                reason_payment += " "+month_name+" "+payment_year
            file_data += reason_payment.ljust(30, " ")     
            file_data +="\n"      
        gentextfile = base64.b64encode(bytes(file_data,'utf-8'))
        self.file_data = gentextfile
        self.file_name = file_name

    def bbva_tsc_pcs_file_format(self):
        file_data = ''
        file_name = 'BBVA BANCOMER NET CASH​ ​ (TSC or PSC).txt'
        
        for payment in self.payment_ids:
            #==== Receipt Bank DATA ===========#            
            if payment.payment_bank_account_id:
                file_data += payment.payment_bank_account_id.acc_number.zfill(18)
            else:
                temp =''
                file_data +=temp.zfill(18)
            if payment.journal_id.bank_account_id:
                file_data += payment.journal_id.bank_account_id.acc_number.zfill(18)
            else:
                temp =''
                file_data +=temp.zfill(18)
            #====== Currency Data =========#
            if payment.currency_id:
                file_data += payment.currency_id.name
            #====== Amount Data =========#
            amount = round(payment.amount, 2)
            amount = str(amount).split('.')
            file_data +=str(amount[0]).zfill(13)
            file_data +='.'
            file_data +=str(amount[1]).zfill(2)

            #=====“Beneficiary”======#
            beneficiary_name=''
            if payment.partner_id:
                beneficiary_name = payment.partner_id.name
            file_data += beneficiary_name.ljust(30, " ")   
            #======= Type of Account ========#
            if payment.payment_bank_account_id:
                if payment.payment_bank_account_id.account_type=='card':
                    file_data += '03'
                elif payment.payment_bank_account_id.account_type=='clabe_acc':
                    file_data += '40'
                else:
                    file_data += '00'
            #======= Bank Code / Key bank ========#
            if payment.payment_bank_id:
                bank_code = ''
                if payment.payment_bank_id.l10n_mx_edi_code:
                    bank_code = payment.payment_bank_id.l10n_mx_edi_code
                file_data += bank_code.zfill(3)
            #=====reason for payment======#
            reason_payment = 'PAGO'
            if payment.payment_date:
                payment_year = str(payment.payment_date.year)[:2]
                month_name = format_datetime(payment.payment_date, 'MMMM', locale=get_lang(self.env).code)
                reason_payment += " "+month_name+" "+payment_year
            file_data += reason_payment.ljust(30, " ")     
            #====== net_cash_reference =======#
            net_cash_reference = ''
            if payment.net_cash_reference:
                net_cash_reference = payment.net_cash_reference
            file_data += net_cash_reference.zfill(7)
            #====== net_cash_availability =======#   
            if payment.net_cash_availability:
                if payment.net_cash_availability=='SPEI':
                    file_data += 'H'
                elif payment.net_cash_availability=='CECOBAN':
                    file_data += 'M'
            file_data +="\n"      
                                     
        gentextfile = base64.b64encode(bytes(file_data,'utf-8'))
        self.file_data = gentextfile
        self.file_name = file_name

    def bbva_sit_file_format(self):
        file_data = ''
        file_name = 'BBVA BANCOMER SIT.txt'
        
        #============= Header Data =========#
        file_data += 'H'
        file_data += '000747289'
        
        #========= Current Date =========
        currect_time = datetime.today()
        file_data +=str(currect_time.year)
        file_data +="-"+str(currect_time.month).zfill(2)
        file_data +="-"+str(currect_time.day)
        
        file_data += '01'
        
        #===== sit_file_key ====
        sit_file_key = ''
#         if payment.sit_file_key:
#             sit_file_key = payment.sit_file_key
        file_data +=sit_file_key.ljust(30)
        #======== Response Code =======#
        file_data += '00'
        #======== Response code description =======#
        file_data += ''.ljust(20)
        #======= Channel =======#
        file_data += ''.ljust(3)
        #========= Charge account ==========#
        if self.journal_id.bank_account_id:
            file_data += self.journal_id.bank_account_id.acc_number.zfill(35)
        else:
            temp =''
            file_data +=temp.zfill(35)
        #====== Currency of the agreement =======#
        file_data += ''.ljust(3)
        #======== FILLER =========
        file_data += ''.ljust(1251)
        file_data +="\n"

        #============= Payment  Details =========#              
        for payment in self.payment_ids:

            #=======Registration indicato ========            
            file_data +="D"
            #=======Instruction ========            
            file_data +="A"
            #=======Document type ========            
            file_data +="P"
            #=== Reference  =====
            folio = ''
            if payment.folio:
                folio = payment.folio
            folio_splits = folio.split('/')
            rec_data = ''
            for sp_data in folio_splits:
                rec_data+=sp_data
            file_data += rec_data.ljust(20)
            #===== Provider Password / Beneficiary Password =======#
            pass_beneficiary = ''
            if payment.partner_id and payment.partner_id.password_beneficiary:
                pass_beneficiary = payment.partner_id.password_beneficiary
            file_data += pass_beneficiary.ljust(30)
            #======= Type of Service  =======
            file_data +="PDA"
            
            #======= Operation code  ========#
            sit_operation_code = '0'
            if payment.sit_operation_code:
                if payment.sit_operation_code=='payment_on_account_bancomer':
                    sit_operation_code = '2'
                elif payment.sit_operation_code=='payment_interbank':
                    sit_operation_code = '5'
            file_data +=sit_operation_code
            #======== Charge account  ==========#
            file_data += ''.zfill(20)
            #======== FILLER ========
            file_data += ''.ljust(15)
            #=======Reference numeral ========#
            sit_reference = ''
            if payment.sit_operation_code and payment.sit_operation_code=='payment_interbank' and payment.sit_reference:
                sit_reference = payment.sit_reference
            file_data += sit_reference.ljust(25)
            #=======Reason For Payment ========#
            sit_reason_for_payment = ''
            if payment.sit_operation_code and payment.sit_operation_code=='payment_interbank' and payment.sit_reason_for_payment:
                sit_reason_for_payment = payment.sit_reason_for_payment
            file_data += sit_reason_for_payment.ljust(37)
            #======== FILLER ========
            file_data += ''.ljust(15)
    
            #=======Personalized legend ========#
            sit_reference = ''
            if payment.sit_reference:
                sit_reference = payment.sit_reference
            file_data += sit_reference.ljust(25)
            #======== CIE Concept ========#
            file_data += ''.ljust(37)
            #======Tax receipt =====#
            file_data += "N"
            #======== FILLER ========#
            file_data += ''.ljust(8)
            #======= Account type ======#
            file_data += ''.ljust(2)
            #======= Subscription account ======#
            file_data += ''.ljust(35)
            #======= Name of 1st beneficiary ======#
            file_data += ''.ljust(40)
            #======= Identification code of the 1st beneficiary======#
            file_data += ''.ljust(1)
            #======= Identification number 1st beneficiary======#
            file_data += ''.ljust(30)
            #======= Name of 2nd beneficiary======#
            file_data += ''.ljust(40)
            #======= Identification code of the 2nd beneficiary======#
            file_data += ''.ljust(1)
            #======= Identification number 2nd beneficiary======#
            file_data += ''.ljust(30)
            #====== Currency Data =========#
            if payment.currency_id:
                if payment.currency_id.name=='MXN':
                    file_data += 'MXP'
                else:
                    file_data += payment.currency_id.name
            #====== BIC / SWIFT =========#
            if payment.currency_id:
                if payment.currency_id.name=='MXN':
                    file_data += ''.ljust(11)
                else:
                    if payment.payment_bank_account_id and payment.payment_bank_account_id.bic_swift:
                        file_data += payment.payment_bank_account_id.bic_swift.ljust(11)
                    else:
                        file_data += ''.ljust(11)                         

            #====== ABA =========#
            if payment.currency_id:
                if payment.currency_id.name=='MXN':
                    file_data += ''.ljust(9)
                else:
                    if payment.payment_bank_account_id and payment.payment_bank_account_id.aba:
                        file_data += payment.payment_bank_account_id.aba.zfill(9)
                    else:
                        file_data += ''.zfill(9)                         
        
            #======= Document key ========#
            file_data += 'FA'
            #====== Amount Data =========
            amount = round(payment.amount, 2)
            amount = str(amount).split('.')
            file_data +=str(amount[0]).zfill(13)
            file_data +=str(amount[1]).zfill(2)
            #========FILLER==========
            file_data +=''.zfill(15)
            #======= Confirmation Type ========#
            file_data += '01'
            #========== Email ==========#
            email = ''
            if payment.partner_id and payment.partner_id.email:
                email =  payment.partner_id.email
            file_data += email.ljust(50)
            #===== Periodicity interest of ======#
            file_data += 'N'
            #======= FILLER =======#
            file_data +=''.zfill(8)
            #======= FILLER =======#
            file_data +=''.zfill(4)

            #========= Payment Date =========
            if payment.payment_date:
                file_data +=str(payment.payment_date.year)
                file_data +="-"+str(payment.payment_date.month).zfill(2)
                file_data +="-"+str(payment.payment_date.day)
            #====== Effective date =======#
            file_data += '0001-01-01'
            #====== Grace Date =======#
            file_data += '0001-01-01'
            #====== Expiration date=======#
            file_data += '0001-01-01'
            #=========Document Date =========
            if payment.payment_date:
                file_data +=str(payment.payment_date.year)
                file_data +="-"+str(payment.payment_date.month).zfill(2)
                file_data +="-"+str(payment.payment_date.day)
            #====== Recurring payment indicator =========#
            file_data += 'N'
            #======= FILLER =======#
            file_data += ''.ljust(1) 
            #====== Recurring payment end date=======#
            file_data += '0001-01-01'
            #==== Additional data length or Payment detail =====#
            file_data += '700'
            #======== Additional =======#
            additional = 'PAGO UNAM'
            if payment.folio:
                split_data = payment.folio.split('/')
                if split_data:
                    additional +=" - "+split_data[0]
            if payment.sit_additional_data:
                additional += payment.sit_additional_data
            file_data += additional.ljust(700)
            #======= FILLER =======#
            file_data += ''.ljust(10) 
            #======= FILLER =======#
            file_data += ''.ljust(10)
            #======= Code status of the document =======# 
            file_data += ''.ljust(2)
            #======= Document status code description =======# 
            file_data += ''.ljust(30)
            #====== Date of last document event=======#
            file_data += '0001-01-01'
            file_data +="\n"
        gentextfile = base64.b64encode(bytes(file_data,'utf-8'))
        self.file_data = gentextfile
        self.file_name = file_name
        
    def santander_file_format(self):
        file_name = 'SANTANDER.txt'
        file_data = ''
        for payment in self.payment_ids:
            #========= Charge account ==========#
            if self.journal_id.bank_account_id:
                file_data += self.journal_id.bank_account_id.acc_number.zfill(11)
            else:
                temp =''
                file_data +=temp.zfill(11)
            #====== Spaces ====#
            file_data += ''.ljust(5)
            #===== Bank Account Payment Receiving ========#
            if payment.payment_bank_account_id:
                file_data += payment.payment_bank_account_id.acc_number.zfill(11)
            else:
                temp =''
                file_data +=temp.zfill(11)
            #====== Spaces ====#
            file_data += ''.ljust(5)
            #====== Amount Data =========#
            amount = round(payment.amount, 2)
            amount = str(amount).split('.')
            file_data +=str(amount[0]).zfill(10)
            file_data +='.'
            file_data +=str(amount[1]).zfill(2)
            #======= Payment concept ==========#
            santander_payment_concept = ''
            if payment.santander_payment_concept:
                santander_payment_concept = payment.santander_payment_concept
            file_data += santander_payment_concept.ljust(40)
            
            #==== Payment Date ======
            if payment.payment_date:
                file_data +=str(payment.payment_date.day)
                file_data +=str(payment.payment_date.month).zfill(2)
                file_data +=str(payment.payment_date.year)[:2]
            file_data +="\n"
        gentextfile = base64.b64encode(bytes(file_data,'utf-8'))
        self.file_data = gentextfile
        self.file_name = file_name
            
    def hsbc_file_format(self):    
        file_name = 'HSBC.csv'
        file_data = ''
        gentextfile = base64.b64encode(bytes(file_data,'utf-8'))
        self.file_data = gentextfile
        self.file_name = file_name
                 
    def generate_bank_layout(self):
#        for payment in self.payment_ids:
#             if payment.journal_id.id != self.journal_id.id:
#                 raise UserError(_("The selected layout does NOT match the bank of the selected payments"))
        if self.journal_id.bank_format == 'banamex':
            self.banamex_file_format()
        elif self.journal_id.bank_format == 'bbva_tnn_ptc':
            self.bbva_tnn_ptc_file_format()
        elif self.journal_id.bank_format == 'bbva_tsc_pcs':
            self.bbva_tsc_pcs_file_format()
        elif self.journal_id.bank_format == 'bbva_sit':
            self.bbva_sit_file_format()
        elif self.journal_id.bank_format == 'santander':
            self.santander_file_format()
#        elif self.journal_id.bank_format == 'hsbc':
#            self.hsbc_file_format()
        
        return {
            'name': _('Generate Bank Layout'),
            'res_model': 'generate.bank.layout',
            'res_id' : self.id,
            'view_mode': 'form',
            'target': 'new',
            'type': 'ir.actions.act_window',
        }    
    
    
    
    
