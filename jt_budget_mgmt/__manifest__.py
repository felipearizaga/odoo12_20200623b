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
    'summary': 'Budget Management System for UNAM',
    'version': '13.0.0.1.1',
    'category': 'Accounting',
    'author': 'Jupical Technologies Pvt. Ltd.',
    'maintainer': 'Jupical Technologies Pvt. Ltd.',
    'website': 'http://www.jupical.com',
    'license': 'AGPL-3',
    'depends': ['account', 'project', 'jt_conac'],
    'data': [
        # Security Files
        'security/ir.model.access.csv',

        # Data Files
        'data/data.xml',

        # Program Code Views
        'views/program_code_views/program_view.xml',
        'views/program_code_views/sub_program_view.xml',
        'views/program_code_views/dependency_view.xml',
        'views/program_code_views/sub_dependency_view.xml',
        'views/program_code_views/expenditure_item_view.xml',
        'views/program_code_views/verifying_digit_view.xml',
        'views/program_code_views/resource_origin_view.xml',
        'views/program_code_views/institutional_activity_view.xml',
        'views/program_code_views/budget_program_conversion_view.xml',
        'views/program_code_views/shcp_code_view.xml',
        'views/program_code_views/departure_conversion_view.xml',
        'views/program_code_views/expense_type_view.xml',
        'views/program_code_views/geographic_location_view.xml',
        'views/program_code_views/key_wallet_view.xml',
        'views/program_code_views/project_type_view.xml',
        'views/program_code_views/stages_view.xml',
        'views/program_code_views/agreement_type_view.xml',

        # Root Views
        'views/year_configuration_view.xml',
        'views/code_structure_view.xml',
        'views/project_project_view.xml',
        'views/program_code_view.xml',
        'views/expenditure_budget_view.xml',
        'views/adequacies_view.xml',
        'views/standardization_view.xml',

        # Wizard Files
        'wizard/import_line_view.xml',
        'wizard/reject_view.xml',
        'wizard/reject_standardization_line_view.xml',
        'wizard/import_standardization_line_view.xml',
        'wizard/import_assigned_amount_line_view.xml',
        'wizard/import_adequacies_line_view.xml',
        'wizard/affect_payment_budget_wiz_view.xml',

        # Main Menu File
        'views/budget_menus.xml',
    ],
    'demo': [
        'demo/demo_code_structure.xml',
        'demo/demo_year_configuration.xml',
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
}
