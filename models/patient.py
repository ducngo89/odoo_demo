# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

# override function create partner


class ResPartners(models.Model):
    _inherit = 'res.partner'
    @api.model
    def create(self, vals_list):
        res = super(ResPartners, self).create(vals_list)
        print('yes working')
        # do something with res.partner
        return res


class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'
    patient_name = fields.Char(string='Patient Name')


class HospitalPatient(models.Model):
    _name = 'hospital.patient'
    _description = 'Patient Record'
    # init chatter
    _inherit = ['mail.thread.cc', 'mail.activity.mixin']
    # init Record name
    _rec_name = 'patient_name'
    _order = "id desc"

    def name_get(self):
        res = []
        for rec in self:
            res.append((rec.id, '[%s] %s' %
                        (rec.name_seq, rec.patient_name)))
        return res

    @api.constrains('patient_age')
    def check_age(self):
        for rec in self:
            if rec.patient_age <= 5:
                raise ValidationError(_('The age must be Grater then 5'))

    @api.depends('patient_age')
    def set_age_group(self):
        for rec in self:
            if rec.patient_age is not None:
                if rec.patient_age < 18:
                    rec.age_group = 'minor'
                else:
                    rec.age_group = 'major'

    def open_patient_appointments(self):
        return {
            'name': _('Appointments'),
            'domain': [('patient_id', '=', self.id)],
            'view_type': 'form',
            'res_model': 'hospital.appointment',
            'view_id': False,
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',
        }

    def get_appointment_count(self):
        count = self.env['hospital.appointment'].search_count(
            [('patient_id', '=', self.id)])
        self.appointment_count = count

    patient_name = fields.Char(string='Name', required=True)
    patient_age = fields.Integer('Age', track_visibility="always")
    notes = fields.Text(string='Notes')
    image = fields.Binary(string='Image', attachment=True)

    email_id = fields.Char(string='Email')

    appointment_count = fields.Integer(
        string="Appointment", compute="get_appointment_count")

    active = fields.Boolean("Active", default=True)

    doctor_id = fields.Many2one(
        'hospital.doctor', string="Doctor")

    user_id = fields.Many2one(
        'res.users', string="PRO")

    # auto name
    name_seq = fields.Char(string='Patient ID', required=True,
                           copy=False, readonly=True, index=True, default=lambda self: _('New'))
    gender = fields.Selection([
        ('male', 'Male'),
        ('fe_male', 'Female')
    ], default='male', string='Gender')

    doctor_gender = fields.Selection([
        ('male', 'Male'),
        ('fe_male', 'Female')
    ], default='male', string='Doctor Gender')

    age_group = fields.Selection(
        [('major', 'Major'), ('minor', 'Minor')], string='Age Group', compute='set_age_group')

    @api.onchange('doctor_id')
    def set_doctor_gender(self):
        for rec in self:
            if(rec.doctor_id):
                rec.doctor_gender = rec.doctor_id.gender

    @api.model
    def create(self, vals):
        # auto name
        if vals.get('name_seq', _('New')) == _('New'):
            vals['name_seq'] = self.env['ir.sequence'].next_by_code(
                'hospital.patient.sequence') or _('New')
        # end auto name
        result = super(HospitalPatient, self).create(vals)
        return result

    def action_send_card(self):
        print('sending email')
        template_id = self.env.ref('odoo_demo.patient_card_email_template').id
        self.env['mail.template'].browse(
            template_id).send_mail(self.id, force_send=True)

    patient_name_upper = fields.Char(compute="_compute_upper_name",inverse="_inverse_upper_name",string="Patient Name Upper")

    @api.depends("patient_name")
    def _compute_upper_name(self):
        for rec in self:
            rec.patient_name_upper = rec.patient_name.upper() if rec.patient_name else False

    def _inverse_upper_name(self):
        for rec in self:
            rec.patient_name = rec.patient_name_upper.lower() if rec.patient_name_upper else False