from odoo import models, fields,_
from odoo.exceptions import UserError, ValidationError
import base64
from datetime import datetime, timedelta
from odoo.tools.misc import formatLang, format_date, get_lang
from babel.dates import format_datetime, format_date

class GenerateBankPayrollPayment(models.TransientModel):

    _name = 'generate.bank.layout.payroll.payment'
    _description = 'Generate Bank Layout Payroll Payment'

    bank_layout = fields.Selection([('SANTANDER','SANTANDER'),
                                    ('HSBC','HSBC'),
                                    ],string="Layout")
    employee_ids = fields.Many2many('hr.employee','hr_employee_bank_payroll_payment_rel','bank_layout_id','emp_id','Employee')
    file_name = fields.Char('Filename')
    file_data = fields.Binary('Download')

    def action_generate_bank_layout(self):
        active_ids = self.env.context.get('active_ids')
        if not active_ids:
            return ''
        
        return {
            'name': _('Generate Bank Layout'),
            'res_model': 'generate.bank.layout.payroll.payment',
            'view_mode': 'form',
            'view_id': self.env.ref('jt_payroll_payment.view_generate_bank_layout_payroll_payment').id,
            'context': {'default_employee_ids':[(6,0,active_ids)]},
            'target': 'new',
            'type': 'ir.actions.act_window',
        }    
    def santander_file_format(self):

        file_data = ''
        file_name = 'SANTANDER.txt'
        #===== Type Of Registation ======#
        file_data += '1'
        #===== Sequence Number =======#
        file_data += '00001'
        #====== Sense =========#
        file_data += 'E'
        #====== Generation Date =========#
        currect_time = datetime.today()
        file_data +=str(currect_time.month).zfill(2)
        file_data +=str(currect_time.day)
        file_data +=str(currect_time.year)
        #======= Account ========= TODO#
        file_data += "".ljust(16)
        #===== Application Date ======= TODO#
        currect_time = datetime.today()
        file_data +=str(currect_time.month).zfill(2)
        file_data +=str(currect_time.day)
        file_data +=str(currect_time.year)
        file_data += "\n"
        next_no = 2
        total_record = len(self.employee_ids) 
        
        for emp in self.employee_ids:
            #===== Type Of Records ======#
            file_data += "2"
            #======= Sequence Number ======#
            file_data += "0000"
            file_data += str(next_no)
            next_no += 1
            #===== Employee Number =======#
            file_data += "".ljust(7)
            #===== Patemal Surname =======#
            file_data += "".ljust(30)
            #===== Matemal Surname =======#
            file_data += "".ljust(20)
            #===== Name =======#
            file_data += "".ljust(30)
            #===== Bank account ======= TODO#
            file_data += "".ljust(16)
            #========= Amount =======TODO#
            file_data += "".ljust(16)
            
            file_data += "\n"
        #===== Type Of Reg=========#
        file_data += "3"
        #===== Sequence Number =======#
        file_data += "0000"
        file_data += str(next_no)
        #====== total_record =======#
        file_data += str(total_record).zfill(5)
        #====== Total Amount ======== TODO#
        file_data += "".ljust(18)
        
        gentextfile = base64.b64encode(bytes(file_data,'utf-8'))
        self.file_data = gentextfile
        self.file_name = file_name
    def hsbc_file_format(self):
        file_data = ''
        file_name = 'HSBC.txt'
        #======= File Format Indication =======#
        file_data += 'MXPRLF'
        #====== Authorization Level ======#
        file_data += 'F'
        #====== Charge Account ==== TODO ====#
        file_data += ''.zfill(10)
        #===== Total Amount ===== TODO#
        file_data += ''.zfill(14) 
        #===== Total Operation ===== TODO#
        file_data += ''.zfill(7) 
        #===== Value Date ===== TODO#
        file_data += '        '
        #===== Batch Reference =====#
        file_data += ''.ljust(34)
        
        for emp in self.employee_ids:
            #===== Beneficiary Account TODO=======#
            file_data += ''.ljust(10) 
            #===== Amount ====== TODO#
            file_data += ''.ljust(14)
            #===== Reference for the account Beneficiary TODO===#
            file_data += ''.ljust(34)
            #===== Name of the Benefiaciry TODO =====#
            file_data += ''.ljust(35)
            
        gentextfile = base64.b64encode(bytes(file_data,'utf-8'))
        self.file_data = gentextfile
        self.file_name = file_name
        
    def generate_bank_layout(self):
        if self.bank_layout == 'SANTANDER':
            self.santander_file_format()
        elif self.bank_layout == "HSBC":
            self.hsbc_file_format()
        
        return {
            'name': _('Generate Bank Layout'),
            'res_model': 'generate.bank.layout.payroll.payment',
            'res_id' : self.id,
            'view_mode': 'form',
            'target': 'new',
            'type': 'ir.actions.act_window',
        }    
