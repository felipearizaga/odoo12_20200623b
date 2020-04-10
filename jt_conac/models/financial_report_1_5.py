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
from odoo import models, _, fields


class MXReportAccountCoaCONAC(models.AbstractModel):
    _name = "jt_conac.coa.conac.report"
    _inherit = "account.coa.report"
    _description = "Mexican CONAC Chart of Account Report"

    def _get_templates(self):
        templates = super(MXReportAccountCoaCONAC, self)._get_templates()
        templates[
            'main_table_header_template'] = 'account_reports.main_table_header'
        templates['main_template'] = 'account_reports.main_template'
        return templates

    def _get_columns_name(self, options):
        return [
            {'name': _('Account Name')},
            {'name': _('Nature')},
            {'name': _('Account Type')},
            {'name': _('Gender')},
            {'name': _('Group')},
            {'name': _('Item')},
        ]

    def _get_lines(self, options, line_id=None):
        conac_obj = self.env['coa.conac']
        lines = []
        hierarchy_lines = conac_obj.sudo().search(
            [('parent_id', '=', False)], order='code')

        for line in hierarchy_lines:

            # Root Level
            lines.append({
                'id': 'hierarchy_' + line.code,
                'name': line.display_name,
                'columns': [{'name': ''}, {'name': ''}, {'name': ''}, {'name': ''}, {'name': ''}],
                'level': 1,
                'unfoldable': False,
                'unfolded': True,
            })

            # Level-1 lines
            level_1_lines = conac_obj.search([('parent_id', '=', line.id)])
            for level_1_line in level_1_lines:
                lines.append({
                    'id': 'level_one_%s' % level_1_line.id,
                    'name': level_1_line.display_name,
                    'columns': [{'name': ''}, {'name': ''}, {'name': ''}, {'name': ''}, {'name': ''}],
                    'level': 2,
                    'unfoldable': True,
                    'unfolded': True,
                    'parent_id': 'hierarchy_' + line.code,
                })

                # Level-2 Lines
                level_2_lines = conac_obj.search(
                    [('parent_id', '=', level_1_line.id)])
                for level_2_line in level_2_lines:
                    lines.append({
                        'id': 'level_two_%s' % level_2_line.id,
                        'name': level_2_line.display_name,
                        'columns': [{'name': ''}, {'name': ''}, {'name': ''}, {'name': ''}, {'name': ''}],
                        'level': 3,
                        'unfoldable': True,
                        'unfolded': True,
                        'parent_id': 'level_one_%s' % level_1_line.id,
                    })

                    # Level-3 Lines
                    level_3_lines = conac_obj.search(
                        [('parent_id', '=', level_2_line.id)])
                    for level_3_line in level_3_lines:
                        nature = ''
                        acc_type = ''
                        if level_3_line == 'debtor':
                            nature = 'Debitable account'
                            acc_type = 'Debtor'
                        elif level_3_line == 'creditor':
                            nature = 'Creditable account'
                            acc_type = 'Creditor'
                        elif nature == 'debtor_creditor':
                            nature = 'Debitable/Creditable account'
                            acc_type = 'Debtoror/Creditor'
                        lines.append({
                            'id': 'level_three_%s' % level_3_line.id,
                            'name': level_3_line.display_name,
                            'columns': [{'name': nature}, {'name': acc_type}, {'name': level_3_line.gender}, {'name': level_3_line.group}, {'name': level_3_line.item}],
                            'level': 4,
                            'parent_id': 'level_two_%s' % level_2_line.id,
                        })
        return lines

    def _get_report_name(self):
        """The structure to name the CoA CONAC reports is:
        YEAR_MONTH_COA_CONAC"""
        context = self.env.context
        date_report = fields.Date.from_string(context['date_from']) if context.get(
            'date_from') else fields.date.today()
        return '%s_%s_COA_CONAC' % (
            date_report.year,
            str(date_report.month).zfill(2))
