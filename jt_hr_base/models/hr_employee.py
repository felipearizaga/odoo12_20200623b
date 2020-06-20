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
from odoo.exceptions import UserError

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    worker_payment_key = fields.Integer('Worker Payment Key')
    # journal_id = fields.Many2one('account.journal', string='Bank Key Scatter')
    payment_place_id = fields.Many2one('payment.place', 'Payment Place')

    # Job Information Page Fields
    entry_date = fields.Date('Date of Entry')
    ss_number = fields.Integer('Social Security Number')
    worker_type = fields.Selection([('base', 'Base'), ('trust', 'Trust'),
                                    ('pensioner', 'Pensioner')],
                                   string='Type of Worker')
    worker_status = fields.Selection([('active', 'Active'),
                                      ('license', 'License')],
                                     string='Worker Status')
    occ_code = fields.Selection([('commerce', 'Commerce'), ('drivers', 'Drivers'),
                                 ('admin_worker', 'Administrative Workers'),
                                 ('edu_workers', 'Education Workers'),
                                 ('trab_del', 'Trab. del Arte, Espe'),
                                 ('prot_serve', 'T. in servs of prot'),
                                 ('fab_worker', 'Fabrile Workers'),
                                 ('technician', 'Technicians'),
                                 ('salaried_proff', 'Salaried Professional'),
                                 ('independent_proff', 'Independent Professional'),
                                 ('public_off', 'Public institution or company official'),
                                 ('private_off',
                                  'Private institution or company official'),
                                 ('pensioner', 'Retirees or pensioners')],
                                string='National Occupation Code')
    registration = fields.Selection([('confirmed', 'Confirmed'), (
        'rejected', 'Rejected')], string='Registration in Financial Institution')

    # Private Information Page Fields
    street = fields.Char('Street')
    street2 = fields.Char('Street 2')
    city = fields.Char('City')
    state_id = fields.Many2one('res.country.state', string='State')
    zip_code = fields.Char('Zip')
    country_id = fields.Many2one('res.country', string='Country')
    rfc = fields.Char('RFC')
    housing = fields.Selection([('house', 'House'), ('building', 'Building'),
                                ('department', 'Department'),
                                ('housing_unit', 'Housing Unit'),
                                ('market', 'Market')], string='Type of housing')
    road = fields.Selection([('old_road', 'Old Road'), ('andador', 'Andador'),
                             ('highway', 'Highway'), ('avenue', 'Avenue'),
                             ('boulevard', 'Boulevard'), ('street', 'Street'),
                             ('closed_circuit', 'Closed Circuit'),
                             ('alley_road', 'Alley Road'),
                             ('high_road', 'High Road'),
                             ('carriage_way', 'Carriage Way'),
                             ('roundabout', 'Roundabout'), ('stroll', 'Stroll'),
                             ('prolongation', 'Prolongation'),
                             ('private_return', 'Private Return'),
                             ('valley', 'Valley via Town')], string='Type of Road')

    marital = fields.Selection(
        selection_add=[('free_union', 'Free Union'), ('separate', 'Separate')])
    certificate = fields.Selection(
        selection_add=[('without_school', 'Without schooling'),
                       ('primary', 'Primary'), ('secondary', 'Secondary'),
                       ('preparatory', 'Preparatory'),
                       ('diploma', 'Diplomat-specialty'),
                       ('career_tech', 'Career Technical'),
                       ('not_school', 'Not in school')], string='Schooling')
    profession = fields.Selection([('phy_anthropologist', 'Physical anthropologist'),
                                   ('soc_anthropologist', 'Social anthropologist'),
                                   ('architect', 'Architect'),
                                   ('biologist', 'Biologist'), ('cardinal', 'Cardinal'),
                                   ('dental', 'Dental surgeon'),
                                   ('accountant', 'Public Accountant'),
                                   ('ethnologist', 'Ethnologist'),
                                   ('physicist', 'Physicist'),
                                   ('physicist_math', 'Physicist mathematical'),
                                   ('general', 'General'), ('lieutenant', 'Lieutenant'),
                                   ('engineer', 'Engineer'), ('licensed', 'Licensed'),
                                   ('doctor', 'Doctor'), ('professor', 'Professor')],
                                  string='Profession')
    nationality = fields.Selection([('mexican', 'Mexican'),
                                    ('north_american', 'North American'),
                                    ('lebanese', 'Lebanese'),
                                    ('south_american', 'South American'),
                                    ('american_central', 'American Central'),
                                    ('europe', 'Europe'), ('israelite', 'Israelite'),
                                    ('japanese', 'Japanese'), ('canadian', 'Canadian'),
                                    ('other', 'Other')], string='Nationality')

    # HR Settings Page Fields
    worker_number = fields.Char('Worker Number')
    place_number = fields.Integer('Number of Place')

    # Accounting Page Fields
    beneficiary_ids = fields.Many2many('res.partner', string='Beneficiary')
    bank_ids = fields.One2many("res.partner.bank", 'employee_id', string="Bank Accounts")
    account_receivable_id = fields.Many2one(
        'account.account', string='Account receivable')
    account_payable_id = fields.Many2one(
        'account.account', string='Account payable')

    @api.onchange('branch_number')
    def onchange_branch_number(self):
        if self.branch_number:
            if not self.branch_number.isdigit():
                raise UserError(
                    _('The Branch Number should only consist of digits.'))
            if len(self.branch_number) > 4:
                raise UserError(
                    _('The Branch Number should be of 4 digits only.'))
            if len(self.branch_number) < 4:
                self.branch_number = self.branch_number.zfill(4)

    _sql_constraints = [
        ('worker_number_uniq', 'unique (worker_number)', 'The Worker Number must be unique.')]

class ResPartnerBank(models.Model):

    _inherit = 'res.partner.bank'

    employee_id = fields.Many2one('hr.employee')