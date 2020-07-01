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
from datetime import datetime
from odoo import models, _


class StatementOfFinancialPosition(models.AbstractModel):
    _name = "jt_conac.financial.position.report"
    _inherit = "account.report"
    _description = "Statement of Financial Position"

    filter_date = {'date_from': '', 'date_to': '', 'filter': 'this_year'}
    filter_comparison = {'date_from': '', 'date_to': '', 'filter': 'no_comparison', 'number_period': 1}
    filter_journals = True
    filter_all_entries = True
    filter_journals = True
    filter_unfold_all = True
    filter_hierarchy = True
    filter_analytic = None

    def _get_columns_name(self, options):
        columns = [{'name': _('Account Name')}]

        comparison = options.get('comparison')
        periods = []
        if comparison and comparison.get('filter') != 'no_comparison':
            periods = [period.get('string') for period in comparison.get('periods')]
        columns.extend([{'name': period} for period in periods])

        return columns

    def _get_lines(self, options, line_id=None):
        move_line_obj = self.env['account.move.line']
        comparison = options.get('comparison')
        periods = []
        if comparison and comparison.get('filter') != 'no_comparison':
            periods = [period.get('string') for period in comparison.get('periods')]
        conac_obj = self.env['coa.conac']
        lines = []
        hierarchy_lines = conac_obj.sudo().search(
            [('parent_id', '=', False)], order='code')

        posted = 'draft'
        if options.get('unposted_in_period'):
            posted = 'posted'

        for line in hierarchy_lines:
            if line.code in ('1.0.0.0', '2.0.0.0', '3.0.0.0'):
                lines.append({
                    'id': 'hierarchy_' + line.code,
                    'name': line.display_name,
                    'columns': [{'name': ''} for period in periods],
                    'level': 1,
                    'unfoldable': False,
                    'unfolded': True,
                })

                level_1_lines = conac_obj.search([('parent_id', '=', line.id)])
                for level_1_line in level_1_lines:
                    main_balance_dict = {}
                    lines.append({
                        'id': 'level_one_%s' % level_1_line.id,
                        'name': level_1_line.display_name,
                        'columns': [{'name': ''} for period in periods],
                        'level': 2,
                        'unfoldable': False,
                        'unfolded': True,
                        'parent_id': 'hierarchy_' + line.code,
                    })

                    level_2_lines = conac_obj.search([('parent_id', '=', level_1_line.id)])
                    for level_2_line in level_2_lines:
                        period_dict = {}
                        level_3_lines = conac_obj.search([('parent_id', '=', level_2_line.id)])
                        balance = 0
                        for period in comparison.get('periods'):
                            date_start = datetime.strptime(str(period.get('date_from')), '%Y-%m-%d').date()
                            date_end = datetime.strptime(str(period.get('date_to')), '%Y-%m-%d').date()

                            move_lines = move_line_obj.sudo().search(
                                [('coa_conac_id', '=', level_2_line.id),
                                 ('move_id.state', '=', posted),
                                 ('date', '>=', date_start), ('date', '<=', date_end)])
                            if move_lines:
                                balance += (sum(move_lines.mapped('debit')) - sum(move_lines.mapped('credit')))
                                period_dict.update({period.get('string'): balance})
                        for level_3_line in level_3_lines:
                            for period in comparison.get('periods'):
                                date_start = datetime.strptime(str(period.get('date_from')), '%Y-%m-%d').date()
                                date_end = datetime.strptime(str(period.get('date_to')), '%Y-%m-%d').date()

                                move_lines = move_line_obj.sudo().search([('coa_conac_id', '=', level_3_line.id),
                                                        ('move_id.state', '=', posted),
                                                        ('date', '>=', date_start), ('date', '<=', date_end)])
                                if move_lines:
                                    balance += (sum(move_lines.mapped('debit')) - sum(move_lines.mapped('credit')))
                                    period_dict.update({period.get('string'): balance})
                        for pd, bal in period_dict.items():
                            if pd in main_balance_dict.keys():
                                main_balance_dict.update({pd: main_balance_dict.get(pd) + bal})
                            else:
                                main_balance_dict.update({pd: bal})
                        lines.append({
                            'id': 'level_two_%s' % level_2_line.id,
                            'name': level_2_line.display_name,
                            'columns': [{'name': period_dict.get(period) if period in period_dict.keys() else 0} for period in periods],
                            'level': 3,
                            'parent_id': 'level_one_%s' % level_1_line.id,
                        })
                    lines.append({
                        'id': 'total_%s' % level_1_line.id,
                        'name': 'Total',
                        'columns': [{'name': main_balance_dict.get(period) if period in main_balance_dict.keys() else 0} for period in periods],
                        'level': 2,
                        'title_hover': level_1_line.display_name,
                        'unfoldable': False,
                        'unfolded': True,
                        'parent_id': 'hierarchy_' + line.code,
                    })
        return lines
