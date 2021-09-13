from odoo import models, api, fields, _
from odoo.exceptions import ValidationError
from string import ascii_lowercase, digits
from random import choice


class HumanCoupon(models.Model):
    _inherit = "coupon.coupon"

    _code_mask = "xxxxx-00"
    _forbidden_characters = "i1o0"
    _dedup_max_retries = 20

    def _generate_code_from_mask(self):
        def unmask(char):
            # x means a random character
            if char == "x":
                return choice(
                    [
                        char
                        for char in ascii_lowercase
                        if char not in self._forbidden_characters
                    ]
                )

            # 0 means a random digit
            if char == "0":
                return choice(digits)
            return char

        return "".join([unmask(char) for char in self._code_mask])

    @api.model
    def _generate_code(self):
        """Generate a more human readable coupon."""
        # Inherits https://github.com/odoo/odoo/blob/14.0/addons/coupon/models/coupon.py#L15
        # This method doesn't call super since it's only the code generation

        code = self._generate_code_from_mask()
        retries = 0
        while len(self.env["coupon.coupon"].search([("code", "=", code)])):
            code = self._generate_code_from_mask()
            retries += 1
            if retries > self._dedup_max_retries:
                raise ValidationError(
                    _("Unable to generate a non existing random coupon code.")
                )

        return code

    # code is overidden here because the default need to be this _generate_code
    code = fields.Char(default=_generate_code, required=True, readonly=True)
