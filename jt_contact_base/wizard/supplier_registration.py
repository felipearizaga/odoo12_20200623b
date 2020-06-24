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
import base64
import csv
import io
import os
from datetime import datetime
from odoo import fields, models

class SupplierRegistration(models.TransientModel):
    _name = 'supplier.registration'
    _description = 'Supplier Registration'

    layout = fields.Selection([('banamex', 'Banamex'),
                               ('bbva', 'BBVA Bancomer SIT'), ('hsbc', 'HSBC'),
                               ('santander', 'Santander')], string='Layout')
    fec_data = fields.Binary('FEC File', readonly=True, attachment=False)
    filename = fields.Char(string='Filename', size=256, readonly=True)

    def generate(self):
        partners = self.env['res.partner'].search(
            [('id', 'in', self._context.get('active_ids'))])
        if self.layout == 'banamex':
            filename = 'Banamex.txt'
            name = 'Banamex'
            contents = ""
            for partner in partners:
                contents += "03"
                if partner.account_type:
                    if partner.account_type == 'checks':
                        contents += "01"
                        if partner.branch_number:
                            contents += str(partner.branch_number).zfill(4)
                    if partner.account_type == 'card':
                        contents += "03"
                        if partner.branch_number:
                            contents += "0000"
                    if partner.account_type == 'master_acc':
                        contents += "06"
                        if partner.branch_number:
                            contents += "0000"
                if partner.bank_ids:
                    contents += partner.bank_ids[:1].acc_number.zfill(20)
                if partner.currency_id:
                    if partner.currency_id.name == 'MXN':
                        contents += "001"
                    if partner.currency_id.name == 'USD':
                        contents += "005"
                contents += "000"
                contents += datetime.now().date().strftime('%d%m%y')
                contents += datetime.now().time().strftime('%H%M')
                contents += '\n\n'

        if self.layout == 'bbva':
            filename = 'BBVA Bancomer SIT.txt'
            name = 'BBVA Bancomer SIT'
            contents = ""
            for partner in partners:
                contents += "H000747289"
                contents += datetime.now().date().strftime('%Y-%m-%d')
                contents += "01"
                contents += "00                       "
                if partner.bank_ids[:1].acc_number:
                    contents += partner.bank_ids[:1].acc_number.zfill(35)
                contents += "   "
                contents += "                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   "
                contents += "DAP"
                if partner.password:
                    contents += partner.password
                contents += "PDA"
                contents += "00000000000000000000"
                contents += "000000000000000"
                contents += "               "
                contents += "                         "
                contents += "                                     "
                contents += "N          "
                contents += "                                  "
                contents += "                                       "
                contents += "                              "
                contents += "                                      "
                contents += "                            "
                if partner.currency_id:
                    if partner.currency_id.name == 'MXN':
                        contents += "MXN"
                        if partner.bic_swift:
                            contents += partner.bic_swift.zfill(11)
                    if partner.currency_id.name == 'USD':
                        contents += "USD"
                        if partner.aba:
                            contents += partner.aba.zfill(9)
                    if partner.currency_id.name == 'EUR':
                        contents += "EUR"
                        if partner.aba:
                            contents += partner.aba.zfill(9)
                    if partner.currency_id.name == "CAD":
                        contents += "CAD"
                        if partner.aba:
                            contents += partner.aba.zfill(9)
                    if partner.currency_id.name == "CHF":
                        contents += "CHF"
                        if partner.aba:
                            contents += partner.aba.zfill(9)
                    if partner.currency_id.name == "SEK":
                        contents += "SEK"
                        if partner.aba:
                            contents += partner.aba.zfill(9)
                    if partner.currency_id.name == "GBP":
                        contents += "GBP"
                        if partner.aba:
                            contents += partner.aba.zfill(9)
                    if partner.currency_id.name == "JPY":
                        contents += "JPY"
                        if partner.aba:
                            contents += partner.aba.zfill(9)
                contents += "FA"
                contents += "00000000000000001"
                if partner.email and len(partner.email) < 50:
                    contents += partner.email.ljust(50)
                contents += "N000000000000"
                contents += "0001-01-010001-01-010001-01-01"
                contents += "N 0001-01-01700"
                contents += "                      "
                contents += "                              0001-01-01"
                contents += '\n\n'

        if self.layout == 'hsbc':
            name = 'HSBC'
            with open('HSBC.csv', mode='w') as file:
                writer = csv.writer(file, delimiter=',',
                                    quotechar='\'', quoting=csv.QUOTE_MINIMAL)
                for partner in partners:
                    lst = []
                    if partner.bank_ids[:1].acc_number:
                        lst.append(partner.bank_ids[:1].acc_number.zfill(10))
                    if partner.password:
                        lst.append(partner.password.zfill(10))
                    if partner.currency_id.name == 'MXN':
                        lst.append(1)
                    if partner.currency_id.name == 'USD':
                        lst.append(1)
                    lst.append(0)
                    lst.append('                  ')
                    lst.append('             ')
                    lst.append('Transfer third parties')
                    writer.writerow(tuple(lst))
            with open('HSBC.csv', 'r', encoding="utf-8") as f2:
                data = str.encode(f2.read(), 'utf-8')
            self.write({
                'fec_data': base64.encodestring(data),
                'filename': 'HSBC.csv',
            })

        if self.layout == 'santander':
            filename = 'Santander.txt'
            name = 'Santander'
            contents = ""
            for partner in partners:
                contents += "     "
                if partner.bank_ids[:1].acc_number:
                    contents += partner.bank_ids[:1].acc_number.zfill(10)
                contents += "     "
                contents += '\n\n'

        if self.layout != 'hsbc':
            file_data = base64.b64decode(open(os.path.dirname(
                os.path.abspath(__file__)) + "/newfile.txt", "rb").read())
            content = io.StringIO(file_data.decode("utf-8")).read()
            content += contents
            self.write({
                'fec_data': base64.b64encode(content.encode('utf-8')),
                'filename': filename,
            })
        return {
            'name': name,
            'type': 'ir.actions.act_url',
            'url': "web/content/?model=supplier.registration&id=" + str(self.id) + "&filename_field=filename&field=fec_data&download=true&filename=" + self.filename,
            'target': 'self',
        }
