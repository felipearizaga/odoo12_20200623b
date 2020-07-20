from odoo import models, fields, api

class BankTransferRequest(models.Model):

    _name = 'bank.transfer.request'
    
    batch_folio = fields.Integer("Batch Folio")
    application_date = fields.Date("Application Date")
    bank_id = fields.Many2one('res.bank','Bank')
    bank_account_id = fields.Many2one('res.partner.bank','Destination Account')
    currency_id = fields.Many2one('res.currency','Currency')
    amount = fields.Float('Transfer Amount requested')
    area_req_transfer = fields.Char('Area requesting transfer')
    user_id = fields.Many2one('res.users','Requesting User')
    req_transfer = fields.Char('Required Transfer')
    operation_type_id = fields.Many2one('operation.type', "Type Operation")
    observation = fields.Char('Observation')