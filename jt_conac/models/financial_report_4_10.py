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
import unicodedata
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

class StatesAndProgramReports(models.AbstractModel):
    _name = "jt_conac.states.and.program.report"
    _inherit = "account.coa.report"
    _description = "States and Program Reports"

    def _get_templates(self):
        templates = super(
            StatesAndProgramReports, self)._get_templates()
        templates[
            'main_table_header_template'] = 'account_reports.main_table_header'
        templates['main_template'] = 'account_reports.main_template'
        return templates

    def _get_columns_name(self, options):
        return [
            {'name': _('Concepto')},
            {'name': _('Aprobado')},
            {'name': _('Ampliaciones/ (Reducciones)')},
            {'name': _('Modificado')},
            {'name': _('Devengado')},
            {'name': _('Pagado')},
            {'name': _('Subejercicio')},
        ]

    def strip_accents(self, text):
        return ''.join(char for char in
                       unicodedata.normalize('NFKD', text)
                       if unicodedata.category(char) != 'Mn')

    def _get_lines(self, options, line_id=None):
        states_obj = self.env['states.program']
        bud_obj = self.env['expenditure.budget']
        adeq_obj = self.env['adequacies']
        adequacies = adeq_obj.search([('state', '=', 'accepted')])
        budget = bud_obj.search([('state', '=', 'validate')])
        if options.get('date') and 'period_type' in options.get('date'):
            if options.get('date').get('period_type') == 'fiscalyear':
                date_from = options.get('date').get('date_from')
                date_to = options.get('date').get('date_to')
                if isinstance(date_from, str):
                    date_from = datetime.strptime(date_from, DEFAULT_SERVER_DATE_FORMAT).date()
                if isinstance(date_to, str):
                    date_to = datetime.strptime(date_to, DEFAULT_SERVER_DATE_FORMAT).date()
                budget = bud_obj.search([('state', '=', 'validate'),
                                         ('from_date', '=', date_from),
                                         ('to_date', '=', date_to)])
        prog_dict_auth = {}
        prog_dict_ade = {}
        date_from = False
        date_to = False
        if options.get('date'):
            date_from = options.get('date').get('date_from')
            date_to = options.get('date').get('date_to')
        if isinstance(date_from, str):
            date_from = datetime.strptime(date_from, DEFAULT_SERVER_DATE_FORMAT).date()
        if isinstance(date_to, str):
            date_to = datetime.strptime(date_to, DEFAULT_SERVER_DATE_FORMAT).date()
        for line in budget.success_line_ids:
            if line.program_code_id and line.program_code_id.budget_program_conversion_id and \
                    line.program_code_id.budget_program_conversion_id.desc:
                prog_name = line.program_code_id.budget_program_conversion_id.desc.upper()
                prog_name = self.strip_accents(prog_name)
                shcp = line.program_code_id.budget_program_conversion_id.shcp
                if prog_name in prog_dict_auth.keys():
                    prog_dict = prog_dict_auth.get(prog_name)[0]
                    if shcp in prog_dict.keys():
                        amt = prog_dict.get(shcp)
                        prog_dict.update({shcp: amt + line.authorized})
                    else:
                        prog_dict.update({shcp: line.authorized})
                else:
                    prog_dict_auth.update({prog_name: [{shcp: line.authorized}]})
        for ade in adequacies:
            if ade.adaptation_type == 'liquid' and ade.date_of_liquid_adu >= date_from and ade.date_of_liquid_adu <= date_to:
                for line in ade.adequacies_lines_ids:
                    if line.program:
                        prog_name = line.program.budget_program_conversion_id.desc.upper()
                        prog_name = self.strip_accents(prog_name)
                        shcp = line.program.budget_program_conversion_id.shcp.name
                        if prog_name in prog_dict_ade.keys():
                            shcp_dict = prog_dict_ade.get(prog_name)[0]
                            if shcp in shcp_dict.keys():
                                if line.line_type == 'increase':
                                    shcp_dict.update({shcp: shcp_dict.get(shcp) + line.amount})
                                else:
                                    shcp_dict.update({shcp: shcp_dict.get(shcp) - line.amount})
                            else:
                                if line.line_type == 'increase':
                                    shcp_dict.update({shcp: line.amount})
                                else:
                                    shcp_dict.update({shcp: -line.amount})
                        else:
                            if line.line_type == 'increase':
                                prog_dict_ade.update({prog_name: [{shcp: line.amount}]})
                            else:
                                prog_dict_ade.update({prog_name: [{shcp: -line.amount}]})

            elif ade.adaptation_type != 'liquid' and ade.date_of_budget_affected >= date_from and ade.date_of_budget_affected <= date_to:
                for line in ade.adequacies_lines_ids:
                    if line.program:
                        prog_name = line.program.budget_program_conversion_id.desc.upper()
                        prog_name = self.strip_accents(prog_name)
                        shcp = line.program.budget_program_conversion_id.shcp.name
                        if prog_name in prog_dict_ade.keys():
                            shcp_dict = prog_dict_ade.get(prog_name)[0]
                            if shcp in shcp_dict.keys():
                                if line.line_type == 'increase':
                                    shcp_dict.update({shcp: shcp_dict.get(shcp) + line.amount})
                                else:
                                    shcp_dict.update({shcp: shcp_dict.get(shcp) - line.amount})
                            else:
                                if line.line_type == 'increase':
                                    shcp_dict.update({shcp: line.amount})
                                else:
                                    shcp_dict.update({shcp: -line.amount})
                        else:
                            if line.line_type == 'increase':
                                prog_dict_ade.update({prog_name: [{shcp: line.amount}]})
                            else:
                                prog_dict_ade.update({prog_name: [{shcp: -line.amount}]})

        lines = []
        hierarchy_lines = states_obj.sudo().search([('parent_id', '=', False)], order='code')

        main_total_auth = 0
        main_total_ade = 0
        main_total_mod = 0
        main_total_sub = 0

        for line in hierarchy_lines:
            lines.append({
                'id': 'hierarchy_' + line.code,
                'name': line.concept,
                'columns': [{'name': ''}, {'name': ''}, {'name': ''},
                            {'name': ''}, {'name': ''}, {'name': ''}],
                'level': 1,
                'unfoldable': False,
                'unfolded': True,
            })
            level_1_lines = states_obj.search([('parent_id', '=', line.id)])
            for level_1_line in level_1_lines:
                lines.append({
                        'id': 'level_one_%s' % level_1_line.id,
                    'name': level_1_line.concept,
                    'columns': [{'name': ''}, {'name': ''}, {'name': ''},
                                {'name': ''}, {'name': ''}, {'name': ''}],
                    'level': 2,
                    'unfoldable': True,
                    'unfolded': True,
                    'parent_id': 'hierarchy_' + line.code,
                })
                level_2_lines = states_obj.search([('parent_id', '=', level_1_line.id)])
                for level_2_line in level_2_lines:
                    total_auth = 0
                    total_ade = 0
                    total_mod = 0
                    total_sub = 0
                    lines.append({
                        'id': 'level_two_%s' % level_2_line.id,
                        'name': level_2_line.concept,
                        'columns': [{'name': ''}, {'name': ''}, {'name': ''},
                                    {'name': ''}, {'name': ''}, {'name': ''}],
                        'level': 3,
                        'unfoldable': True,
                        'unfolded': True,
                        'parent_id': 'level_one_%s' % level_1_line.id,
                    })

                    line_concept = level_2_line.concept.upper()
                    line_concept = self.strip_accents(line_concept)
                    if line_concept in prog_dict_auth.keys():
                        concept_dict = prog_dict_auth.get(line_concept)[0]
                        prog_dict_con = dict(sorted(concept_dict.items()))
                        for shcp, authorized in prog_dict_con.items():
                            name = shcp.name
                            if shcp.desc:
                                name += ' '
                                name += shcp.desc
                            adeq_amt = 0
                            if line_concept in prog_dict_ade.keys():
                                shcp_dict = prog_dict_ade.get(line_concept)[0]
                                if shcp.name in shcp_dict.keys():
                                    adeq_amt = shcp_dict.get(shcp.name)
                            modi_amt = authorized + adeq_amt
                            lines.append({
                                'id': 'level_three_%s' % shcp.id,
                                'name': name,
                                'columns': [{'name': '%.2f' % authorized, 'style': 'margin-left:15px;'},
                                            {'name': '%.2f' % adeq_amt, 'style': 'margin-left:15px;'},
                                            {'name': '%.2f' % modi_amt, 'style': 'margin-left:15px;'},
                                            {'name': ''},
                                            {'name': ''},
                                            {'name': '%.2f' % modi_amt, 'style': 'margin-left:15px;'}],
                                'level': 4,
                                'unfoldable': False,
                                'unfolded': False,
                                'parent_id': 'level_two_%s' % level_2_line.id,
                            })
                            total_auth += authorized
                            total_ade += adeq_amt
                            total_mod += modi_amt
                            total_sub += modi_amt

                        lines.append({
                            'id': 'level_three_%s' % shcp.id,
                            'name': _('Total'),
                            'columns': [{'name': '%.2f' % total_auth, 'style': 'margin-left:15px;'},
                                        {'name': '%.2f' % total_ade, 'style': 'margin-left:15px;'},
                                        {'name': '%.2f' % total_mod, 'style': 'margin-left:15px;'}, {'name': ''},
                                        {'name': ''}, {'name': '%.2f' % total_sub, 'style': 'margin-left:15px;'}],
                            'level': 5,
                            'class': 'total',
                            'unfoldable': False,
                            'unfolded': False,
                            'parent_id': 'level_two_%s' % level_2_line.id,
                        })
                        main_total_auth += total_auth
                        main_total_ade += total_ade
                        main_total_mod += total_mod
                        main_total_sub += total_sub

                    # level_3_lines = states_obj.search(
                    #     [('parent_id', '=', level_2_line.id)])
                    # for level_3_line in level_3_lines:
                    #     print("Inside-=-=-= -=-=", level_3_line.concept)
                    #     lines.append({
                    #         'id': 'level_three_%s' % level_3_line.id,
                    #         'name': level_3_line.concept,
                    #         'columns': [{'name': level_3_line.approved}, {'name': level_3_line.ext_and_red}, {'name': level_3_line.modified}, {'name': level_3_line.accrued}, {'name': level_3_line.paid_out}, {'name': level_3_line.sub_exercise}],
                    #         'level': 4,
                    #         'parent_id': 'level_two_%s' % level_2_line.id,
                    #     })
        lines.append({
            'id': 'hierarchy_' + line.code,
            'name': 'Main Total',
            'columns': [{'name': main_total_auth}, {'name': main_total_ade}, {'name': main_total_mod},
                        {'name': ''}, {'name': ''}, {'name': main_total_sub}],
            'level': 1,
            'unfoldable': False,
            'unfolded': True,
        })
        return lines
