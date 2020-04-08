# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, _, fields, tools
from odoo.exceptions import ValidationError
from odoo.tools.safe_eval import safe_eval
from odoo.tools.xml_utils import _check_with_xsd

MX_NS_REFACTORING = {
    'catalogocuentas__': 'catalogocuentas',
    'BCE__': 'BCE',
}

CFDICOA_TEMPLATE = 'jt_conac.cfdicoa_conac'
CFDICOA_XSD = 'l10n_mx_reports/data/xsd/%s/cfdicoa.xsd'
CFDICOA_XSLT_CADENA = 'l10n_mx_reports/data/xslt/%s/CatalogoCuentas_1_2.xslt'


class MXReportAccountCoaCONAC(models.AbstractModel):
    _name = "jt_conac.coa.conac.report"
    _inherit = "jt_conac.conac.trial.report"
    _description = "Mexican CONAC Chart of Account Report"

    filter_comparison = None
    filter_all_entries = None
    filter_hierarchy = None
    filter_journals = None

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

    def _post_process(self, grouped_accounts, initial_balances, options, comparison_table):
        afrl_obj = self.env['account.financial.html.report.line']
        lines = []
        n_cols = len(comparison_table) * 2 + 2
        total = [0.0] * n_cols
        afr_lines = afrl_obj.search([
            ('parent_id', '=', False),
            ('code', 'ilike', 'CONAC_MX_COA_%')], order='code')
        for line in afr_lines:
            childs = self._get_lines_second_level(
                line.children_ids, grouped_accounts, initial_balances, options, comparison_table)
            if not childs:
                continue
            cols = ['']
            if not options.get('coa_conac_only'):
                cols = cols * n_cols
                child_cols = [c['columns'] for c in childs if c.get('level') == 2]
                total_line = []
                for col in range(n_cols):
                    total_line += [sum(a[col] for a in child_cols)]
                    total[col] += total_line[col]
                for child in childs:
                    child['columns'] = [{'name': self.format_value(v)} for v in child['columns']]
            lines.append({
                'id': 'hierarchy_' + line.code,
                'name': line.name,
                'columns': [{'name': v} for v in cols],
                'level': 1,
                'unfoldable': False,
                'unfolded': True,
            })
            lines.extend(childs)
            if not options.get('coa_conac_only'):
                lines.append({
                    'id': 'total_%s' % line.code,
                    'name': _('Total %s') % line.name[2:],
                    'level': 0,
                    'class': 'hierarchy_total',
                    'columns': [{'name': self.format_value(v)} for v in total_line],
                })
        if not options.get('coa_conac_only'):
            lines.append({
                'id': 'hierarchy_total',
                'name': _('Total'),
                'level': 0,
                'class': 'hierarchy_total',
                'columns': [{'name': self.format_value(v)} for v in total],
            })
        return lines

    def _get_lines_fourth_level(self, accounts, grouped_accounts, initial_balances, options, comparison_table):
        lines = []
        company_id = self.env.context.get('company_id') or self.env.company
        is_zero = company_id.currency_id.is_zero
        for account in accounts:
            # skip accounts with all periods = 0 (debit and credit) and no initial balance
            if not options.get('coa_conac_only'):
                non_zero = False
                for period in range(len(comparison_table)):
                    if account in grouped_accounts and (
                        not is_zero(initial_balances.get(account, 0)) or
                        not is_zero(grouped_accounts[account][period]['debit']) or
                        not is_zero(grouped_accounts[account][period]['credit'])
                    ):
                        non_zero = True
                        break
                if not non_zero:
                    continue
            name = account.code + " " + account.name
            name = name[:63] + "..." if len(name) > 65 else name
            tag = account.tag_ids.filtered(lambda r: r.color == 4)
            if len(tag) > 1:
                raise UserError(_(
                    'The account %s is incorrectly configured. Only one tag is allowed.'
                ) % account.name)
            nature = dict(tag.fields_get()['nature']['selection']).get(tag.nature, '')
            cols = [{'name': nature}]
            if not options.get('coa_conac_only'):
                cols = self._get_cols(initial_balances, account, comparison_table, grouped_accounts)
            lines.append({
                'id': account.id,
                'parent_id': 'level_two_%s' % tag.id,
                'name': name,
                'level': 4,
                'columns': cols,
                'caret_options': 'account.account',
            })
        return lines

    def _get_lines(self, options, line_id=None):
        print("3..................", options, line_id)
        options['coa_conac_only'] = True
        lines = self._post_process({}, {}, options, [])

        # lines = [
        #     {
        #         'id': '111',
        #         'name': '1.0.0.0 Activo',
        #         'columns': [
        #             {
        #                 'name': ''
        #             }
        #         ],
        #         'level': 1,
        #         'unfoldable': False,
        #         'unfolded': True
        #     },
        #     {
        #         'id': '1dstg11',
        #         'name': '2.0.0.0 Pasivo',
        #         'columns': [
        #             {
        #                 'name': ''
        #             }
        #         ],
        #         'level': 1,
        #         'unfoldable': False,
        #         'unfolded': True
        #     },
        #     {
        #         'id': '2454',
        #         'name': '1.1.0.0 Activo Circulante',
        #         'columns': [
        #             {
        #                 'name': ''
        #             }
        #         ],
        #         'level': 2,
        #         'class': '',
        #         'unfoldable': True,
        #         'unfolded': True
        #     },
        #     {
        #         'id': '3fdf',
        #         'parent_id': 'level_one_210',
        #         'name': '1.1.0.0 Activo Circulante',
        #         'columns': [
        #             {
        #                 'name': ''
        #             }
        #         ],
        #         'level': 3,
        #         'unfoldable': True,
        #         'unfolded': True,
        #         # 'tag_id': 1090
        #     },
        #     {
        #         'id': 1,
        #         'parent_id': 'level_two_1090',
        #         'name': '102.01.011 Liquidity Transfer',
        #         'level': 4,
        #         'columns': [
        #             {
        #                 'name': 'Debitable Account',
        #             }
        #         ],
        #         'caret_options': 'account.account'
        #     }
        # ]

        return lines

    # def _get_coa_conac_dict(self, options):
    #     print("4..................")
    #     print("CALL.......................")
    #     xml_data = self._get_lines(options)
    #     accounts = []
    #     account_lines = [l for l in xml_data
    #                      if l.get('level') in [2, 3]]
    #     tag_obj = self.env['account.account.tag']
    #     for line in account_lines:
    #         if line.get('level') == 2:
    #             parent = line
    #             print_parent = True
    #             continue
    #         tag_id = line.get('tag_id', False)
    #         tag = tag_obj.browse(tag_id)
    #         if not tag:
    #             msg = _(
    #                 'This XML could not be generated because some accounts '
    #                 'are not correctly configured and can not be added in '
    #                 'this report.')
    #             raise ValidationError(msg)
    #         if print_parent:
    #             name = parent.get('name').split(' ', 1)
    #             accounts.append({
    #                 'code': name[0],
    #                 'number': name[0],
    #                 'name': name[-1],
    #                 'level': '1',
    #                 'nature': tag.nature,
    #                 'acc_type': line.user_type_id.name,
    #                 'gender': line.gender,
    #                 'group': line.group_id and line.group_id.name or '',
    #                 'item': line.item,
    #             })
    #             print_parent = False
    #         name = line.get('name').split(' ', 1)
    #         accounts.append({
    #             'code': name[0],
    #             'number': name[0],
    #             'name': name[-1],
    #             'level': '2',
    #             'nature': tag.nature,
    #             'acc_type': line.user_type_id.name,
    #             'gender': line.gender,
    #             'group': line.group_id and line.group_id.name or '',
    #             'item': line.item,
    #         })
    #     ctx = self._set_context(options)
    #     date = fields.Date.from_string(ctx['date_from'])
    #     print("ACCOUNTS...............", accounts)

    #     # Add top level lines
    #     chart = {
    #         'vat': self.env.company.vat or '',
    #         'month': str(date.month).zfill(2),
    #         'year': date.year,
    #         'accounts': accounts,
    #     }
    #     return chart

    # def get_xml(self, options):
    #     print("5..................")
    #     qweb = self.env['ir.qweb']
    #     version = '1.3'
    #     ctx = self._set_context(options)
    #     values = self.with_context(ctx)._get_coa_conac_dict(options)
    #     cfdicoa = qweb.render(CFDICOA_TEMPLATE, values=values)
    #     for key, value in MX_NS_REFACTORING.items():
    #         cfdicoa = cfdicoa.replace(key.encode('UTF-8'),
    #                                   value.encode('UTF-8') + b':')
    #     cfdicoa = self._l10n_mx_edi_add_digital_stamp(
    #         CFDICOA_XSLT_CADENA % version, cfdicoa)

    #     with tools.file_open(CFDICOA_XSD % version, "rb") as xsd:
    #         _check_with_xsd(cfdicoa, xsd)
    #     return cfdicoa

    def _get_report_name(self):
        """The structure to name the CoA CONAC reports is:
        YEAR_MONTH_COA_CONAC"""
        context = self.env.context
        date_report = fields.Date.from_string(context['date_from']) if context.get(
            'date_from') else fields.date.today()
        return '%s_%s_COA_CONAC' % (
            date_report.year,
            str(date_report.month).zfill(2))
