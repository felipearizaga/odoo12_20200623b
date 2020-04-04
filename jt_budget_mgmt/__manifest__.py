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
{
    'name': 'Budget Management',
    'summary': 'Finance Budget Management System for UNAM',
    'version': '13.0.0.1.1',
    'category': 'Accounting',
    'author': 'Jupical Technologies Pvt. Ltd.',
    'maintainer': 'Jupical Technologies Pvt. Ltd.',
    'website': 'http://www.jupical.com',
    'license': 'AGPL-3',
    'depends': ['account', 'project'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/import_standardization_line_view.xml',
        'wizard/import_assigned_amount_line_view.xml',
        'wizard/import_adequacies_line_view.xml',
        'wizard/import_line_view.xml',
        'wizard/reject_view.xml',
        'views/standardization_view.xml',
        'views/control_assigned_amounts_view.xml',
        'views/adequacies_view.xml',
        'views/expenditure_budget_view.xml',
        'views/program_code_view.xml',
        #'views/agreement_number_view.xml',
        'views/agreement_type_view.xml',
        'views/stages_view.xml',
        #'views/project_number_view.xml',
        'views/project_type_view.xml',
        'views/key_wallet_view.xml',
        'views/geographic_location_view.xml',
        'views/expense_type_view.xml',
        'views/departure_conversion_view.xml',
        'views/budget_program_conversion_view.xml',
        'views/institutional_activity_view.xml',
        'views/resource_origin_view.xml',
        'views/verifying_digit_view.xml',
        'views/expenditure_item_view.xml',
        'views/sub_dependency_view.xml',
        'views/dependency_view.xml',
        'views/sub_program_view.xml',
        'views/program_view.xml',
        'views/year_view.xml',
        'views/code_structure_view.xml',
        'views/budget_view.xml',
    ],

    'application': False,
    'installable': True,
    'auto_install': False,
}
