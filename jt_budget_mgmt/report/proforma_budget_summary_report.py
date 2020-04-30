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
    _inherit = "account.report"
    _description = "Proforma Budget Summary"

    # filter_program_code = None
    filter_date = {'mode': 'range', 'filter': 'this_month'}
    filter_budget_control = None

    def _get_templates(self):
        templates = super(ProformaBudgetSummaryReport, self)._get_templates()
        templates[
            'main_table_header_template'] = 'account_reports.main_table_header'
        templates['main_template'] = 'jt_budget_mgmt.main_template'
        return templates

    def _get_columns_name(self, options):
        # print("_get_columns_name.............", options)
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
    def _init_filter_budget_control(self, options, previous_options=None):
        options['budget_control'] = []
        options['budget_control'].append({
            'id': 1,
            'name': 'Authorized',
            'code': '01',
            # 'selected': journal_map.get(j.id, j.id in default_group_ids),
        })
        print("init filter budget_control..........", options)

    def get_report_informations(self, options):
        '''
        return a dictionary of informations that will be needed by the js widget, manager_id, footnotes, html of report and searchview, ...
        '''
        options = self._get_options(options)

        searchview_dict = {'options': options, 'context': self.env.context}
        # Check if report needs analytic
        if options.get('analytic_accounts') is not None:
            options['selected_analytic_account_names'] = [self.env['account.analytic.account'].browse(int(account)).name for account in options['analytic_accounts']]
        if options.get('analytic_tags') is not None:
            options['selected_analytic_tag_names'] = [self.env['account.analytic.tag'].browse(int(tag)).name for tag in options['analytic_tags']]
        if options.get('partner'):
            options['selected_partner_ids'] = [self.env['res.partner'].browse(int(partner)).name for partner in options['partner_ids']]
            options['selected_partner_categories'] = [self.env['res.partner.category'].browse(int(category)).name for category in options['partner_categories']]

        # Check whether there are unposted entries for the selected period or not (if the report allows it)
        if options.get('date') and options.get('all_entries') is not None:
            date_to = options['date'].get('date_to') or options['date'].get('date') or fields.Date.today()
            period_domain = [('state', '=', 'draft'), ('date', '<=', date_to)]
            options['unposted_in_period'] = bool(self.env['account.move'].search_count(period_domain))

        if options.get('journals'):
            journals_selected = set(journal['id'] for journal in options['journals'] if journal.get('selected'))
            for journal_group in self.env['account.journal.group'].search([('company_id', '=', self.env.company.id)]):
                if journals_selected and journals_selected == set(self._get_filter_journals().ids) - set(journal_group.excluded_journal_ids.ids):
                    options['name_journal_group'] = journal_group.name
                    break

        report_manager = self._get_report_manager(options)
        info = {'options': options,
                'context': self.env.context,
                'report_manager_id': report_manager.id,
                'footnotes': [{'id': f.id, 'line': f.line, 'text': f.text} for f in report_manager.footnotes_ids],
                'buttons': self._get_reports_buttons_in_sequence(),
                'main_html': self.get_html(options),
                'searchview_html': self.env['ir.ui.view'].render_template(self._get_templates().get('search_template', 'account_report.search_template'), values=searchview_dict),
                }
        return info

    # @api.model
    # def _get_options_program_code(self, options):
    #     program_codes = []
    #     for code_option in options.get('program_codes', []):
    #         if code_option['id'] in ('divider', 'group'):
    #             continue
    #         if code_option['selected']:
    #             program_codes.append(code_option)
    #     print("-----------___>>> ", program_codes)
    #     return program_codes

    # @api.model
    # def _get_options_program_code_domain(self, options):
    #     print("============++>> ")
    #     if not options.get('journals'):
    #         return []

    # def _set_context(self, options):
    #     res = super(ProformaBudgetSummaryReport, self)._set_context(options)
    #     print("_set_context............", res)
    #     return res

    def _get_lines(self, options, line_id=None):
        lines = []

        budget_lines = self.env['expenditure.budget.line'].search([('expenditure_budget_id.state', '=', 'validate')])

        for b_line in budget_lines:
            annual_modified = b_line.authorized + b_line.assigned
            columns = [
                {'name': b_line.authorized},
                {'name': b_line.assigned},
                {'name': annual_modified},
                {'name': 0},
                {'name': 0},
                {'name': 0},
                {'name': 0},
                {'name': 0},
                {'name': b_line.available}
            ]
            lines.append({
                'id': b_line.id,
                'name': b_line.program_code_id.program_code,
                'columns': columns,
                'level': 0,
                'unfoldable': False,
                'unfolded': True,
            })

        return lines
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
