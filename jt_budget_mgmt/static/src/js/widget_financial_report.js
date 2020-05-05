odoo.define('jt_budget_mgmt.widget_financial_report', function (require) {
"use strict";
    var config = require('web.config');
    var core = require('web.core');
    var Dialog = require('web.Dialog');
    var data = require('web.data');
    var Widget = require('web.Widget');
    var RelationalFields = require('web.relational_fields');
    var AccountReport = require('account_reports.account_report');
    var StandaloneFieldManagerMixin = require('web.StandaloneFieldManagerMixin');

    var QWeb = core.qweb;
    var _t = core._t;

    var M2MFilters = Widget.extend(StandaloneFieldManagerMixin, {
        /**
         * @constructor
         * @param {Object} fields
         */
        init: function (parent, fields) {
            this._super.apply(this, arguments);
            StandaloneFieldManagerMixin.init.call(this);
            this.fields = fields;
            this.widgets = {};
        },
        /**
         * @override
         */
        willStart: function () {
            var self = this;
            var defs = [this._super.apply(this, arguments)];
            _.each(this.fields, function (field, fieldName) {
                defs.push(self._makeM2MWidget(field, fieldName));
            });
            return Promise.all(defs);
        },
        /**
         * @override
         */
        start: function () {
            var self = this;
            var $content = $(QWeb.render("m2mWidgetTable", {fields: this.fields}));
            self.$el.append($content);
            _.each(this.fields, function (field, fieldName) {
                self.widgets[fieldName].appendTo($content.find('#'+fieldName+'_field'));
            });
            return this._super.apply(this, arguments);
        },

        //--------------------------------------------------------------------------
        // Private
        //--------------------------------------------------------------------------

        /**
         * This method will be called whenever a field value has changed and has
         * been confirmed by the model.
         *
         * @private
         * @override
         * @returns {Promise}
         */
        _confirmChange: function () {
            var self = this;
            var result = StandaloneFieldManagerMixin._confirmChange.apply(this, arguments);
            var data = {};
            _.each(this.fields, function (filter, fieldName) {
                data[fieldName] = self.widgets[fieldName].value.res_ids;
            });
            this.trigger_up('value_changed', data);
            return result;
        },
        /**
         * This method will create a record and initialize M2M widget.
         *
         * @private
         * @param {Object} fieldInfo
         * @param {string} fieldName
         * @returns {Promise}
         */
        _makeM2MWidget: function (fieldInfo, fieldName) {
            var self = this;
            var options = {};
            options[fieldName] = {
                options: {
                    no_create_edit: true,
                    no_create: true,
                }
            };
            return this.model.makeRecord(fieldInfo.modelName, [{
                fields: [{
                    name: 'id',
                    type: 'integer',
                }, {
                    name: 'display_name',
                    type: 'char',
                }],
                name: fieldName,
                relation: fieldInfo.modelName,
                type: 'many2many',
                value: fieldInfo.value,
            }], options).then(function (recordID) {
                self.widgets[fieldName] = new RelationalFields.FieldMany2ManyTags(self,
                    fieldName,
                    self.model.get(recordID),
                    {mode: 'edit',}
                );
                self._registerWidget(recordID, fieldName, self.widgets[fieldName]);
            });
        },
    });

    var AccountReportInh = AccountReport.include({
        custom_events: {
            'value_changed': function(ev) {
                 var self = this;
                 self.report_options.partner_ids = ev.data.partner_ids;
                 self.report_options.partner_categories = ev.data.partner_categories;
                 self.report_options.analytic_accounts = ev.data.analytic_accounts;
                 self.report_options.code_sections = ev.data.code_sections;
                 self.report_options.analytic_tags = ev.data.analytic_tags;
                 return self.reload().then(function () {
                     self.$searchview_buttons.find('.account_partner_filter').click();
                     self.$searchview_buttons.find('.account_analytic_filter').click();
                     self.$searchview_buttons.find('.program_code_section_filter').click();
                 });
             },
        },

        render_searchview_buttons: function() {
            this._super.apply(this, arguments);

            // program_code_section filter
            if (this.report_options.code_sections) {
                if (!this.M2MFilters) {
                    var fields = {};
                    if (this.report_options.code_sections) {
                        fields['code_sections'] = {
                            label: _t('Programmatic Code Section'),
                            modelName: 'report.program.fields',
                            value: this.report_options.code_sections.map(Number),
                        };
                    }
                    if (!_.isEmpty(fields)) {
                        this.M2MFilters = new M2MFilters(this, fields);
                        this.M2MFilters.appendTo(this.$searchview_buttons.find('.js_program_code_section_m2m'));
                    }
                } else {
                    this.$searchview_buttons.find('.js_program_code_section_m2m').append(this.M2MFilters.$el);
                }
            }

            // program section filter
            if (this.report_options.section_program) {
                if (!this.M2MFilters) {
                    var fields = {};
                    if (this.report_options.section_program) {
                        fields['section_program'] = {
                            label: _t('Program'),
                            modelName: 'program',
                            value: this.report_options.section_program.map(Number),
                        };
                    }
                    if (!_.isEmpty(fields)) {
                        this.M2MFilters = new M2MFilters(this, fields);
                        this.M2MFilters.appendTo(this.$searchview_buttons.find('.js_section_program_m2m'));
                    }
                } else {
                    this.$searchview_buttons.find('.js_section_program_m2m').append(this.M2MFilters.$el);
                }
            }
        },
    });

});