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

    def _get_lines(self, options, line_id=None):
        states_obj = self.env['states.program']
        shcp_obj = self.env['shcp.code']
        bud_obj = self.env['expenditure.budget']
        adeq_obj = self.env['adequacies']
        adequacies = adeq_obj.search([('state', '=', 'accepted')])
        budget = bud_obj.search([('state', '=', 'validate')])
        prog_dict_auth = {'E010': [{}], 'E007': [{}], 'E021': [{}], 'E011': [{}], 'E010-S243-K027-K009': [{}]}
        prog_dict_ade = {}
        for line in budget.success_line_ids:
            prog = line.conversion_program
            if prog == 'E010':
                main_dict = prog_dict_auth.get('E010')[0]
                if prog in main_dict.keys():
                    amt = main_dict.get(prog) + line.authorized
                    main_dict.update({prog: amt})
                else:
                    main_dict.update({prog: line.authorized})
            elif prog == 'E007':
                main_dict = prog_dict_auth.get('E007')[0]
                if prog in main_dict.keys():
                    amt = main_dict.get(prog) + line.authorized
                    main_dict.update({prog: amt})
                else:
                    main_dict.update({prog: line.authorized})
            elif prog == 'E021':
                main_dict = prog_dict_auth.get('E021')[0]
                if prog in main_dict.keys():
                    amt = main_dict.get(prog) + line.authorized
                    main_dict.update({prog: amt})
                else:
                    main_dict.update({prog: line.authorized})
            elif prog == 'E011':
                main_dict = prog_dict_auth.get('E011')[0]
                if prog in main_dict.keys():
                    amt = main_dict.get(prog) + line.authorized
                    main_dict.update({prog: amt})
                else:
                    main_dict.update({prog: line.authorized})
            if prog in ('E010', 'S243', 'K027', 'K009'):
                main_dict = prog_dict_auth.get('E010-S243-K027-K009')[0]
                if prog in main_dict.keys():
                    amt = main_dict.get(prog) + line.authorized
                    main_dict.update({prog: amt})
                else:
                    main_dict.update({prog: line.authorized})
        for ade in adequacies:
            for line in ade.adequacies_lines_ids:
                if line.program:
                    prog = line.program.budget_program_conversion_id.shcp.name
                    if prog in prog_dict_ade.keys():
                        if line.line_type == 'increase':
                            prog_dict_ade.update({prog: prog_dict_ade.get(prog) + line.amount})
                        else:
                            prog_dict_ade.update({prog: prog_dict_ade.get(prog) - line.amount})
                    else:
                        if line.line_type == 'increase':
                            prog_dict_ade.update({prog: line.amount})
                        else:
                            prog_dict_ade.update({prog: -line.amount})

        lines = []
        hierarchy_lines = states_obj.sudo().search([('parent_id', '=', False)], order='code')

        for line in hierarchy_lines:
            lines.append({
                'id': 'hierarchy_' + line.code,
                'name': line.concept,
                'columns': [{'name': ''}, {'name': ''}, {'name': ''}, {'name': ''}, {'name': ''}, {'name': ''}],
                'level': 1,
                'unfoldable': False,
                'unfolded': True,
            })

            level_1_lines = states_obj.search([('parent_id', '=', line.id)])
            for level_1_line in level_1_lines:
                lines.append({
                        'id': 'level_one_%s' % level_1_line.id,
                    'name': level_1_line.concept,
                    'columns': [{'name': ''}, {'name': ''}, {'name': ''}, {'name': ''}, {'name': ''}, {'name': ''}],
                    'level': 2,
                    'unfoldable': True,
                    'unfolded': True,
                    'parent_id': 'hierarchy_' + line.code,
                })

                level_2_lines = states_obj.search([('parent_id', '=', level_1_line.id)])
                for level_2_line in level_2_lines:
                    lines.append({
                        'id': 'level_two_%s' % level_2_line.id,
                        'name': level_2_line.concept,
                        'columns': [{'name': ''}, {'name': ''}, {'name': ''}, {'name': ''}, {'name': ''}, {'name': ''}],
                        'level': 3,
                        'unfoldable': True,
                        'unfolded': True,
                        'parent_id': 'level_one_%s' % level_1_line.id,
                    })
                    if level_2_line.concept == 'Investigación en Humanidades y Ciencias Sociales':
                        prog_dict_E021 = dict(sorted(prog_dict_auth.get('E021')[0].items()))
                        for prog, authorized in prog_dict_E021.items():
                            prog = shcp_obj.search([('name', '=', prog)])
                            name = prog.name
                            if prog.desc:
                                name += ' '
                                name += prog.desc
                            adeq_amt = prog_dict_ade.get(prog.name) if prog_dict_ade.get(prog.name) else 0
                            modi_amt = authorized + adeq_amt
                            lines.append({
                                'id': 'level_three_%s' % prog.id,
                                'name': name,
                                'columns': [{'name': authorized}, {'name': adeq_amt}, {'name': modi_amt}, {'name': ''},
                                            {'name': ''}, {'name': modi_amt}],
                                'level': 4,
                                'unfoldable': False,
                                'unfolded': False,
                                'parent_id': 'level_two_%s' % level_2_line.id,
                            })
                    elif level_2_line.concept == 'Extensión y Difusión Cultural':
                        prog_dict_E011 = dict(sorted(prog_dict_auth.get('E011')[0].items()))
                        for prog, authorized in prog_dict_E011.items():
                            prog = shcp_obj.search([('name', '=', prog)])
                            name = prog.name
                            if prog.desc:
                                name += ' '
                                name += prog.desc
                            adeq_amt = prog_dict_ade.get(prog.name) if prog_dict_ade.get(prog.name) else 0
                            modi_amt = authorized + adeq_amt
                            lines.append({
                                'id': 'level_three_%s' % prog.id,
                                'name': name,
                                'columns': [{'name': authorized}, {'name': adeq_amt}, {'name': modi_amt}, {'name': ''},
                                            {'name': ''}, {'name': modi_amt}],
                                'level': 4,
                                'unfoldable': False,
                                'unfolded': False,
                                'parent_id': 'level_two_%s' % level_2_line.id,
                            })

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

        return lines
