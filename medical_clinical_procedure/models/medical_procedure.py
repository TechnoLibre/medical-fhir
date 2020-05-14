# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class MedicalProcedure(models.Model):
    # FHIR Entity: Procedure (https://www.hl7.org/fhir/procedure.html)
    _name = "medical.procedure"
    _description = "Medical Procedure"
    _inherit = "medical.event"

    internal_identifier = fields.Char(string="Procedure")
    procedure_request_id = fields.Many2one(
        comodel_name="medical.procedure.request",
        string="Procedure request",
        ondelete="restrict",
        index=True,
        readonly=True,
    )  # FHIR Field: BasedOn
    performed_initial_date = fields.Datetime(
        string="Initial date"
    )  # FHIR Field: performed/performedPeriod
    performed_end_date = fields.Datetime(
        string="End date"
    )  # FHIR Field: performed/performedPeriod
    location_id = fields.Many2one(
        comodel_name="res.partner",
        domain=[("is_location", "=", True)],
        ondelete="restrict",
        index=True,
        string="Location",
    )  # FHIR Field: location

    @api.model
    def _generate_from_request(self, request):
        return request.generate_event()

    @api.constrains("procedure_request_id")
    def _check_procedure(self):
        for rec in self:
            # TODO: We need to remove this when timing is defined...
            if len(rec.procedure_request_id.procedure_ids) > 1:
                raise ValidationError(
                    _(
                        "You cannot create more than one Procedure "
                        "for each Procedure Request."
                    )
                )
            if not self.env.context.get("no_check_patient", False):
                if rec.patient_id != rec.procedure_request_id.patient_id:
                    raise ValidationError(_("Patient inconsistency"))

    def _get_internal_identifier(self, vals):
        return self.env["ir.sequence"].next_by_code("medical.procedure") or "/"

    def preparation2in_progress_values(self):
        res = super().preparation2in_progress_values()
        res["performed_initial_date"] = fields.Datetime.now()
        return res

    def in_progress2completed_values(self):
        res = super().in_progress2completed_values()
        res["performed_end_date"] = fields.Datetime.now()
        return res
