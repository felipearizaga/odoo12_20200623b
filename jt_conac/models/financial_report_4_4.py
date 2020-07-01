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
from odoo import models, _
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

class AnalyticalStatusOfAssets(models.AbstractModel):
    _name = "jt_conac.analytical.status.of.assets.report"
    _inherit = "jt_conac.coa.conac.report"
    _description = "Analytical Status of Assets"

    filter_date = {'date_from': '', 'date_to': '', 'filter': 'this_year'}
    filter_comparison = {'date_from': '', 'date_to': '', 'filter': 'no_comparison', 'number_period': 1}
    filter_journals = True
    filter_all_entries = True
    filter_journals = True
    filter_unfold_all = True
    filter_hierarchy = True
    filter_analytic = None

    def _get_columns_name(self, options):
        columns = [
            {'name': _('Concepto')},
            {'name': _('Saldo Inicial')},
            {'name': _('Cargos del Periodo')},
            {'name': _('Abonos del Periodo')},
            {'name': _('Saldo Final')},
            {'name': _('Variación del Periodo')},
        ]

        comparison = options.get('comparison')
        periods = []
        if comparison and comparison.get('filter') != 'no_comparison':
            periods = [period.get('string') for period in comparison.get('periods')]
        columns.extend([{'name': period} for period in periods])

        return columns

    def _get_lines(self, options, line_id=None):
        comparison = options.get('comparison')
        periods = []
        if comparison and comparison.get('filter') != 'no_comparison':
            periods = [period.get('string') for period in comparison.get('periods')]
        conac_obj = self.env['coa.conac']
        move_line_obj = self.env['account.move.line']
        lines = []
        hierarchy_lines = conac_obj.sudo().search(
            [('parent_id', '=', False)], order='code')

        posted = 'draft'
        if options.get('unposted_in_period'):
            posted = 'posted'
        date_from = options.get('date').get('date_from')
        date_to = options.get('date').get('date_to')
        if isinstance(date_from, str):
            date_from = datetime.strptime(date_from, DEFAULT_SERVER_DATE_FORMAT).date()
        if isinstance(date_to, str):
            date_to = datetime.strptime(date_to, DEFAULT_SERVER_DATE_FORMAT).date()

        for line in hierarchy_lines:
            if line.code == '1.0.0.0':
                level_1_columns = [{'name': ''}, {'name': ''}, {'name': ''}, {'name': ''}, {'name': ''}]
                level_1_columns.extend([{'name': ''} for period in periods])

                lines.append({
                    'id': 'hierarchy_' + line.code,
                    'name': line.display_name,
                    'columns': level_1_columns,
                    'level': 1,
                    'unfoldable': False,
                    'unfolded': True,
                })

                level_1_lines = conac_obj.search([('parent_id', '=', line.id)])
                for level_1_line in level_1_lines:
                    level_1_columns = [{'name': ''}, {'name': ''}, {'name': ''}, {'name': ''}, {'name': ''}]
                    lines.append({
                        'id': 'level_one_%s' % level_1_line.id,
                        'name': level_1_line.display_name,
                        'columns': level_1_columns,
                        'level': 2,
                        'unfoldable': True,
                        'unfolded': True,
                        'parent_id': 'hierarchy_' + line.code,
                    })

                    level_2_lines = conac_obj.search([('parent_id', '=', level_1_line.id)])
                    for level_2_line in level_2_lines:
                        level_2_columns = [{'name': ''}, {'name': ''}, {'name': ''}, {'name': ''}, {'name': ''}]
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
                            level_4_lines = conac_obj.search([('parent_id', '=', level_3_line.id)])
                            balance = 0
                            move_lines = move_line_obj.sudo().search([('coa_conac_id', '=', level_3_line.id),
                                 ('move_id.state', '=', posted),
                                 ('date', '>=', date_from), ('date', '<=', date_to)])
                            if move_lines:
                                balance += (sum(move_lines.mapped('debit')) - sum(move_lines.mapped('credit')))

                            for level_4_line in level_4_lines:
                                move_lines = move_line_obj.sudo().search([('coa_conac_id', '=', level_4_line.id),
                                                                          ('move_id.state', '=', posted),
                                                                          ('date', '>=', date_from),
                                                                          ('date', '<=', date_to)])
                                if move_lines:
                                    balance += (sum(move_lines.mapped('debit')) - sum(move_lines.mapped('credit')))

                            level_3_columns = [{'name': ''}, {'name': ''}, {'name': ''}, {'name': ''}, {'name': ''}]
                            level_3_columns.extend([{'name': ''} for period in periods])
                            level_4_columns = [{'name': ''}, {'name': balance}, {'name': ''}, {'name': balance}, {'name': balance}]
                            level_4_columns.extend([{'name': ''} for period in periods])

                            lines.append({
                                'id': 'level_three_%s' % level_3_line.id,
                                'name': level_3_line.display_name,
                                'columns': level_4_columns,
                                'level': 4,
                                'parent_id': 'level_two_%s' % level_2_line.id,
                            })
        return lines
