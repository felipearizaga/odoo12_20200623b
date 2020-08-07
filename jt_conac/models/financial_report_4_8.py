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
from odoo import models, _,api


class AnalyticalIncomeStatement(models.AbstractModel):
    _name = "jt_conac.analytical.income.statement.report"
    _inherit = "account.coa.report"
    _description = "Analytical Income Statement"

    def _get_templates(self):
        templates = super(
            AnalyticalIncomeStatement, self)._get_templates()
        templates[
            'main_table_header_template'] = 'account_reports.main_table_header'
        templates['main_template'] = 'account_reports.main_template'
        return templates

    def _get_columns_name(self, options):
        return [
            {'name': _('Nombre')},
            {'name': _('Estimado')},
            {'name': _('Ampliaciones y Reducciones')},
            {'name': _('Modificado')},
            {'name': _('Devengado')},
            {'name': _('Recaudado')},
            {'name': _('Diferencia')},
        ]

    def _get_lines(self, options, line_id=None):
        income_obj = self.env['income.statement']
        lines = []
        hierarchy_lines = income_obj.sudo().search(
            [('parent_id', '=', False)], order='id')

        for line in hierarchy_lines:
            lines.append({
                'id': 'hierarchy_' + str(line.id),
                'name': line.name,
                'columns': [{'name': ''}, {'name': ''}, {'name': ''}, {'name': ''}, {'name': ''}, {'name': ''}],
                'level': 1,
                'unfoldable': False,
                'unfolded': True,
            })

            level_1_lines = income_obj.search([('parent_id', '=', line.id)])
            for level_1_line in level_1_lines:
                lines.append({
                    'id': 'level_one_%s' % level_1_line.id,
                    'name': level_1_line.name,
                    'columns': [{'name': ''}, {'name': ''}, {'name': ''}, {'name': ''}, {'name': ''}, {'name': ''}],
                    'level': 2,
                    'unfoldable': True,
                    'unfolded': True,
                    'parent_id': 'hierarchy_' + str(line.id),
                })

                level_2_lines = income_obj.search(
                    [('parent_id', '=', level_1_line.id)])
                for level_2_line in level_2_lines:
                    lines.append({
                        'id': 'level_two_%s' % level_2_line.id,
                        'name': level_2_line.name,
                        'columns': [{'name': ''}, {'name': ''}, {'name': ''}, {'name': ''}, {'name': ''}, {'name': ''}],
                        'level': 3,
                        'unfoldable': True,
                        'unfolded': True,
                        'parent_id': 'level_one_%s' % level_1_line.id,
                    })

                    level_3_lines = income_obj.search(
                        [('parent_id', '=', level_2_line.id)])
                    for level_3_line in level_3_lines:
                        lines.append({
                            'id': 'level_three_%s' % level_3_line.id,
                            'name': level_3_line.name,
                            'columns': [{'name': level_3_line.estimated}, {'name': level_3_line.exp_and_red}, {'name': level_3_line.modified}, {'name': level_3_line.accrued}, {'name': level_3_line.raised}, {'name': level_3_line.difference}],
                            'level': 4,
                            'parent_id': 'level_two_%s' % level_2_line.id,
                        })
        return lines

    def _get_report_name(self):
        return _("Analytical Income Statement")

    @api.model
    def _get_super_columns(self, options):
        # date_cols = options.get('date') and [options['date']] or []
        #  date_cols += (options.get('comparison') or {}).get('periods', [])
        #columns = [{'string': _('Initial Balance')}]
        #print ("date_cols=====",date_cols)
        #columns = reversed(date_cols)
        #print ("columns====",columns)
        return {'columns': {}, 'x_offset': 1, 'merge': 1}
 