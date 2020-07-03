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
from odoo import models, api, _
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

class StatementOfChangesInTheFinancialPosition(models.AbstractModel):
    _name = "jt_conac.statement.of.changes.report"
    _inherit = "jt_conac.coa.conac.report"
    _description = "Statement of Changes in the Financial Position"

    filter_date = {'mode': 'range', 'filter': 'this_month'}
    filter_comparison = {'date_from': '', 'date_to': '', 'filter': 'no_comparison', 'number_period': 1}
    filter_all_entries = False
    filter_journals = False
    filter_analytic = False
    filter_unfold_all = False
    filter_cash_basis = None
    filter_hierarchy = False
    filter_unposted_in_period = False
    MAX_LINES = None

    @api.model
    def _get_filter_journals(self):
        # OVERRIDE to filter only bank / cash journals.
        return []

    def _get_templates(self):
        templates = super(StatementOfChangesInTheFinancialPosition, self)._get_templates()
        templates['main_table_header_template'] = 'jt_budget_mgmt.template_statement_fianancial_position_header'
        templates['main_template'] = 'account_reports.main_template'
        return templates

    def _get_columns_name(self, options):
        columns = [{'name': _('Concepto')}]
        if options.get('comparison') and options['comparison'].get('periods'):
            comparison = options.get('comparison')
            period_list = comparison.get('periods')
            period_list.reverse()
            columns += [
                           {'name': _('Origin')},
                           {'name': _('Application')},
                       ] * (len(period_list) + 1)
        else:
            columns = [
                {'name': _('Concepto')}, {'name': _('Origin')},
                           {'name': _('Application')},
            ]
        return columns

    def _get_lines(self, options, line_id=None):
        move_line_obj = self.env['account.move.line']
        conac_obj = self.env['coa.conac']

        comparison = options.get('comparison')
        periods = []
        if comparison and comparison.get('filter') != 'no_comparison':
            period_list = comparison.get('periods')
            period_list.reverse()
            periods = [period for period in period_list]
        periods.append(options.get('date'))

        lines = []
        hierarchy_lines = conac_obj.sudo().search(
            [('parent_id', '=', False)], order='code')

        posted = 'draft'
        if options.get('unposted_in_period'):
            posted = 'posted'

        last_total_dict = {}
        for line in hierarchy_lines:
            if line.code in ('1.0.0.0', '2.0.0.0', '3.0.0.0'):
                lines.append({
                    'id': 'hierarchy_' + line.code,
                    'name': line.display_name,
                    'columns': [{'name': ''}, {'name': ''}] * len(periods),
                    'level': 1,
                    'unfoldable': False,
                    'unfolded': True,
                })

                level_1_lines = conac_obj.search([('parent_id', '=', line.id)])
                for level_1_line in level_1_lines:

                    lines.append({
                        'id': 'level_one_%s' % level_1_line.id,
                        'name': level_1_line.display_name,
                        'columns': [{'name': ''}, {'name': ''}] * len(periods),
                        'level': 2,
                        'unfoldable': False,
                        'unfolded': True,
                        'parent_id': 'hierarchy_' + line.code,
                    })

                    level_2_lines = conac_obj.search([('parent_id', '=', level_1_line.id)])
                    for level_2_line in level_2_lines:
                        main_balance_dict = {}
                        level_2_columns = [{'name': ''}, {'name': ''}] * len(periods)
                        lines.append({
                            'id': 'level_two_%s' % level_2_line.id,
                            'name': level_2_line.display_name,
                            'columns': level_2_columns,
                            'level': 3,
                            'unfoldable': True,
                            'unfolded': True,
                            'parent_id': 'level_one_%s' % level_1_line.id,
                        })

                        level_3_lines = conac_obj.search([('parent_id', '=', level_2_line.id)])
                        for level_3_line in level_3_lines:
                            amt_columns = []
                            period_dict = {}

                            for period in periods:
                                balance = 0
                                date_start = datetime.strptime(str(period.get('date_from')),
                                                               DEFAULT_SERVER_DATE_FORMAT).date()
                                date_end = datetime.strptime(str(period.get('date_to')),
                                                             DEFAULT_SERVER_DATE_FORMAT).date()

                                move_lines = move_line_obj.sudo().search(
                                    [('coa_conac_id', '=', level_3_line.id),
                                     ('move_id.state', '=', posted),
                                     ('date', '>=', date_start), ('date', '<=', date_end)])
                                if move_lines:
                                    balance += (sum(move_lines.mapped('debit')) - sum(move_lines.mapped('credit')))
                                    if period.get('string') in period_dict:
                                        period_dict.update(
                                            {period.get('string'): period_dict.get(period.get('string')) + balance})
                                    else:
                                        period_dict.update({period.get('string'): balance})

                            level_4_lines = conac_obj.search([('parent_id', '=', level_3_line.id)])
                            for level_4_line in level_4_lines:
                                for period in periods:
                                    balance = 0
                                    date_start = datetime.strptime(str(period.get('date_from')),
                                                                   DEFAULT_SERVER_DATE_FORMAT).date()
                                    date_end = datetime.strptime(str(period.get('date_to')),
                                                                 DEFAULT_SERVER_DATE_FORMAT).date()

                                    move_lines = move_line_obj.sudo().search([('coa_conac_id', '=', level_4_line.id),
                                                                              ('move_id.state', '=', posted),
                                                                              ('date', '>=', date_start),
                                                                              ('date', '<=', date_end)])
                                    if move_lines:
                                        balance += (sum(move_lines.mapped('debit')) - sum(move_lines.mapped('credit')))
                                        if period.get('string') in period_dict:
                                            period_dict.update(
                                                {period.get('string'): period_dict.get(period.get('string')) + balance})
                                        else:
                                            period_dict.update({period.get('string'): balance})

                            for pd, bal in period_dict.items():
                                if pd in main_balance_dict.keys():
                                    main_balance_dict.update({pd: main_balance_dict.get(pd) + bal})
                                else:
                                    main_balance_dict.update({pd: bal})
                                if pd in last_total_dict.keys():
                                    last_total_dict.update({pd: last_total_dict.get(pd) + bal})
                                else:
                                    last_total_dict.update({pd: bal})

                            for pe in periods:
                                if pe.get('string') in period_dict.keys():
                                    amt = period_dict.get(pe.get('string'))
                                    amt_columns += [{'name': 0}, {'name': amt}]
                                else:
                                    amt_columns += [{'name': 0}, {'name': 0}]
                            lines.append({
                                'id': 'level_three_%s' % level_3_line.id,
                                'name': level_3_line.display_name,
                                'columns': amt_columns,
                                'level': 4,
                                'parent_id': 'level_two_%s' % level_2_line.id,
                            })
                        total_col = []
                        for pe in periods:
                            if pe.get('string') in main_balance_dict.keys():
                                amt = main_balance_dict.get(pe.get('string'))
                                total_col += [{'name': 0}, {'name': amt}]
                            else:
                                total_col += [{'name': 0}, {'name': 0}]
                        lines.append({
                            'id': 'total_%s' % level_1_line.id,
                            'name': 'Total',
                            'columns': total_col,
                            'level': 2,
                            'title_hover': level_1_line.display_name,
                            'unfoldable': False,
                            'unfolded': True,
                            'parent_id': 'hierarchy_' + line.code,
                        })
        main_total_col = []
        for pe in periods:
            if pe.get('string') in last_total_dict.keys():
                amt = last_total_dict.get(pe.get('string'))
                main_total_col += [{'name': 0}, {'name': amt}]
            else:
                main_total_col += [{'name': 0}, {'name': 0}]
        lines.append({
            'id': 'total_%s' % level_1_line.id,
            'name': 'Main Total',
            'columns': main_total_col,
            'level': 2,
            'title_hover': level_1_line.display_name,
            'unfoldable': False,
            'unfolded': True,
        })
        return lines
