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


class ProformaBudgetSummaryReport(models.AbstractModel):
    _name = "proforma.budget.summary.report"
    _inherit = "account.coa.report"
    _description = "Proforma Budget Summary"

    filter_program_code = None

    def _get_templates(self):
        templates = super(ProformaBudgetSummaryReport, self)._get_templates()
        templates[
            'main_table_header_template'] = 'account_reports.main_table_header'
        templates['main_template'] = 'account_reports.main_template'
        return templates

    def _get_columns_name(self, options):
        return [
            {'name': _('Code program')},
            {'name': _('Authorized')},
            {'name': _('Assigned')},
            {'name': _('Annual Modified')},
            {'name': _('Per Exercise')},
            {'name': _('Committed')},
            {'name': _('Accrued')},
            {'name': _('Exercised')},
            {'name': _('Paid')},
            {'name': _('Available')},
        ]

    @api.model
    def _get_filter_program_code(self):
        print("program code filter..........")
        return self.env['program.code'].search([])

    @api.model
    def _init_filter_program_code(self, options, previous_options=None):
        print("init filter program code..........")
        return False

    @api.model
    def _get_options_program_code(self, options):
        program_codes = []
        for code_option in options.get('program_codes', []):
            if code_option['id'] in ('divider', 'group'):
                continue
            if code_option['selected']:
                program_codes.append(code_option)
        print("-----------___>>> ", program_codes)
        return program_codes

    @api.model
    def _get_options_program_code_domain(self, options):
        print("============++>> ")
        if not options.get('journals'):
            return []

    def _set_context(self, options):
        res = super(ProformaBudgetSummaryReport, self)._set_context(options)
        print("_set_context............", res)
        return res

    # def _get_lines(self, options, line_id=None):
    #     conac_obj = self.env['coa.conac']
    #     lines = []
    #     hierarchy_lines = conac_obj.sudo().search(
    #         [('parent_id', '=', False)], order='code')

    #     for line in hierarchy_lines:

    #         # Root Level
    #         lines.append({
    #             'id': 'hierarchy_' + line.code,
    #             'name': line.display_name,
    #             'columns': [{'name': ''}, {'name': ''}, {'name': ''}, {'name': ''}, {'name': ''}],
    #             'level': 1,
    #             'unfoldable': False,
    #             'unfolded': True,
    #         })

    #         # Level-1 lines
    #         level_1_lines = conac_obj.search([('parent_id', '=', line.id)])
    #         for level_1_line in level_1_lines:
    #             lines.append({
    #                 'id': 'level_one_%s' % level_1_line.id,
    #                 'name': level_1_line.display_name,
    #                 'columns': [{'name': ''}, {'name': ''}, {'name': ''}, {'name': ''}, {'name': ''}],
    #                 'level': 2,
    #                 'unfoldable': True,
    #                 'unfolded': True,
    #                 'parent_id': 'hierarchy_' + line.code,
    #             })

    #             # Level-2 Lines
    #             level_2_lines = conac_obj.search(
    #                 [('parent_id', '=', level_1_line.id)])
    #             for level_2_line in level_2_lines:
    #                 lines.append({
    #                     'id': 'level_two_%s' % level_2_line.id,
    #                     'name': level_2_line.display_name,
    #                     'columns': [{'name': ''}, {'name': ''}, {'name': ''}, {'name': ''}, {'name': ''}],
    #                     'level': 3,
    #                     'unfoldable': True,
    #                     'unfolded': True,
    #                     'parent_id': 'level_one_%s' % level_1_line.id,
    #                 })

    #                 # Level-3 Lines
    #                 level_3_lines = conac_obj.search(
    #                     [('parent_id', '=', level_2_line.id)])
    #                 for level_3_line in level_3_lines:
    #                     nature = ''
    #                     acc_type = ''
    #                     if level_3_line == 'debtor':
    #                         nature = 'Debitable account'
    #                         acc_type = 'Debtor'
    #                     elif level_3_line == 'creditor':
    #                         nature = 'Creditable account'
    #                         acc_type = 'Creditor'
    #                     elif nature == 'debtor_creditor':
    #                         nature = 'Debitable/Creditable account'
    #                         acc_type = 'Debtoror/Creditor'
    #                     lines.append({
    #                         'id': 'level_three_%s' % level_3_line.id,
    #                         'name': level_3_line.display_name,
    #                         'columns': [{'name': nature}, {'name': acc_type}, {'name': level_3_line.gender}, {'name': level_3_line.group}, {'name': level_3_line.item}],
    #                         'level': 4,
    #                         'parent_id': 'level_two_%s' % level_2_line.id,
    #                     })
    #     return lines

    def _get_report_name(self):
        context = self.env.context
        date_report = fields.Date.from_string(context['date_from']) if context.get(
            'date_from') else fields.date.today()
        return '%s_%s_Summary_Report' % (
            date_report.year,
            str(date_report.month).zfill(2))
