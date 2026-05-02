from __future__ import annotations

import re
from abc import abstractmethod
from typing import Any, Dict, List, Optional

from fastapi import HTTPException, Request
from pydantic import BaseModel, ValidationError


class FormRequest:
    """
    Laravel-style Form Request base class.

    Subclass this to create a validated, authorized request object.

    Usage:
        class CreateUserRequest(FormRequest):
            name: str
            email: str
            age: Optional[int] = None

            def rules(self) -> Dict[str, Any]:
                return {
                    "name": ["required", "min:2", "max:100"],
                    "email": ["required", "email"],
                    "age": ["nullable", "min:0"],
                }

            def messages(self) -> Dict[str, str]:
                return {
                    "name.required": "Name is required.",
                    "email.email": "Please provide a valid email address.",
                }

            def authorize(self) -> bool:
                return True  # Override for auth checks

    Then in your route, use FastAPI Depends:

        from fastapi import Depends

        @router.post("/users")
        async def create(request: Request, req: CreateUserRequest = Depends(CreateUserRequest.from_request)):
            validated = req.validated()
            ...
    """

    # -- Internal storage --
    _data: Dict[str, Any] = {}
    _errors: Dict[str, List[str]] = {}
    _validated_data: Dict[str, Any] = {}

    def __init__(self, data: Dict[str, Any]):
        self._data = data
        self._errors = {}
        self._validated_data = {}

    # ---------------------------------------------------------------
    # Override in subclasses
    # ---------------------------------------------------------------

    def rules(self) -> Dict[str, Any]:
        """
        Define validation rules for each field.

        Supported rules:
            required          - Field must be present and non-empty
            nullable          - Field may be None / missing
            string            - Must be a string
            integer / int     - Must be an integer
            numeric / float   - Must be numeric
            boolean / bool    - Must be boolean
            email             - Must be a valid email address
            min:<n>           - Minimum length (strings) or minimum value (numbers)
            max:<n>           - Maximum length (strings) or maximum value (numbers)
            in:<a,b,c>        - Must be one of the listed values
            not_in:<a,b,c>    - Must NOT be one of the listed values
            regex:<pattern>   - Must match regex pattern
            confirmed         - Must match field_confirmation counterpart
            unique:<table>    - (marker – implement custom DB check in authorize/after)
            exists:<table>    - (marker – implement custom DB check in authorize/after)
        """
        return {}

    def messages(self) -> Dict[str, str]:
        """Override to provide custom validation messages."""
        return {}

    def authorize(self) -> bool:
        """
        Override to add authorization logic.
        Return False to raise a 403 Forbidden response.
        """
        return True

    def after(self) -> None:
        """
        Hook called after validation passes.
        Override to add custom post-validation logic.
        """
        pass

    # ---------------------------------------------------------------
    # Public API
    # ---------------------------------------------------------------

    def validated(self) -> Dict[str, Any]:
        """Return only the fields that passed validation."""
        return dict(self._validated_data)

    def get(self, key: str, default: Any = None) -> Any:
        """Get a value from the raw input."""
        return self._data.get(key, default)

    def all(self) -> Dict[str, Any]:
        """Return all raw input data."""
        return dict(self._data)

    def has(self, key: str) -> bool:
        """Check if a key exists in the input."""
        return key in self._data

    def filled(self, key: str) -> bool:
        """Check if a key exists and is not empty."""
        val = self._data.get(key)
        return val is not None and val != "" and val != [] and val != {}

    def errors(self) -> Dict[str, List[str]]:
        """Return validation errors."""
        return dict(self._errors)

    def fails(self) -> bool:
        """Return True if validation failed."""
        return bool(self._errors)

    def passes(self) -> bool:
        """Return True if validation passed."""
        return not self._errors

    # ---------------------------------------------------------------
    # Factory / FastAPI Dependency
    # ---------------------------------------------------------------

    @classmethod
    async def from_request(cls, request: Request) -> "FormRequest":
        """
        FastAPI dependency factory.  Use as:

            req: MyRequest = Depends(MyRequest.from_request)
        """
        try:
            body = await request.json()
        except Exception:
            body = {}

        # Merge query params + body (body takes precedence)
        data: Dict[str, Any] = dict(request.query_params)
        if isinstance(body, dict):
            data.update(body)

        instance = cls(data)

        # Authorization check
        if not instance.authorize():
            raise HTTPException(status_code=403, detail="This action is unauthorized.")

        # Run validation
        instance._run_validation()

        if instance.fails():
            raise HTTPException(status_code=422, detail=instance._errors)

        # Run after hook
        instance.after()

        return instance

    # ---------------------------------------------------------------
    # Validation engine
    # ---------------------------------------------------------------

    def _run_validation(self) -> None:
        """Run all rules against the input data."""
        rules = self.rules()
        custom_messages = self.messages()

        for field, field_rules in rules.items():
            value = self._data.get(field)

            # Normalise rules to a list of strings
            if isinstance(field_rules, str):
                field_rules = [r.strip() for r in field_rules.split("|")]

            is_nullable = "nullable" in field_rules
            is_required = "required" in field_rules

            # Required check
            if is_required and (value is None or value == ""):
                self._add_error(field, "required", custom_messages)
                continue

            # If value is absent and not required, skip remaining rules
            if value is None:
                if is_nullable:
                    self._validated_data[field] = value
                continue

            # Apply each rule
            rule_failed = False
            for rule in field_rules:
                if rule in ("required", "nullable"):
                    continue
                if not self._apply_rule(field, value, rule, custom_messages):
                    rule_failed = True
                    break  # Stop at first failure for this field

            if not rule_failed:
                self._validated_data[field] = value

    def _apply_rule(self, field: str, value: Any, rule: str, custom_messages: Dict[str, str]) -> bool:
        """Apply a single rule to a value. Returns True if the rule passes."""
        rule_name = rule.split(":")[0]
        rule_param = rule[len(rule_name) + 1:] if ":" in rule else None

        if rule_name == "string":
            if not isinstance(value, str):
                self._add_error(field, "string", custom_messages)
                return False

        elif rule_name in ("integer", "int"):
            if not isinstance(value, int) or isinstance(value, bool):
                self._add_error(field, "integer", custom_messages)
                return False

        elif rule_name in ("numeric", "float"):
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                self._add_error(field, "numeric", custom_messages)
                return False

        elif rule_name in ("boolean", "bool"):
            if not isinstance(value, bool):
                self._add_error(field, "boolean", custom_messages)
                return False

        elif rule_name == "email":
            pattern = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
            if not isinstance(value, str) or not pattern.match(value):
                self._add_error(field, "email", custom_messages)
                return False

        elif rule_name == "min":
            n = float(rule_param)
            if isinstance(value, str):
                if len(value) < n:
                    self._add_error(field, f"min:{rule_param}", custom_messages)
                    return False
            elif isinstance(value, (int, float)):
                if value < n:
                    self._add_error(field, f"min:{rule_param}", custom_messages)
                    return False

        elif rule_name == "max":
            n = float(rule_param)
            if isinstance(value, str):
                if len(value) > n:
                    self._add_error(field, f"max:{rule_param}", custom_messages)
                    return False
            elif isinstance(value, (int, float)):
                if value > n:
                    self._add_error(field, f"max:{rule_param}", custom_messages)
                    return False

        elif rule_name == "in":
            allowed = [v.strip() for v in rule_param.split(",")]
            if str(value) not in allowed:
                self._add_error(field, f"in:{rule_param}", custom_messages)
                return False

        elif rule_name == "not_in":
            forbidden = [v.strip() for v in rule_param.split(",")]
            if str(value) in forbidden:
                self._add_error(field, f"not_in:{rule_param}", custom_messages)
                return False

        elif rule_name == "regex":
            try:
                if not re.match(rule_param, str(value)):
                    self._add_error(field, f"regex:{rule_param}", custom_messages)
                    return False
            except re.error:
                self._add_error(field, f"regex:{rule_param}", custom_messages)
                return False

        elif rule_name == "confirmed":
            confirmation_key = f"{field}_confirmation"
            if self._data.get(confirmation_key) != value:
                self._add_error(field, "confirmed", custom_messages)
                return False

        # Marker-only rules (unique, exists) — no engine-level check
        # Users should implement custom checks in authorize() or after()

        return True

    def _add_error(self, field: str, rule: str, custom_messages: Dict[str, str]) -> None:
        """Add a validation error for a field."""
        key = f"{field}.{rule.split(':')[0]}"
        message = custom_messages.get(key) or self._default_message(field, rule)

        if field not in self._errors:
            self._errors[field] = []
        self._errors[field].append(message)

    @staticmethod
    def _default_message(field: str, rule: str) -> str:
        """Generate a human-readable default error message."""
        rule_name = rule.split(":")[0]
        param = rule[len(rule_name) + 1:] if ":" in rule else None
        field_label = field.replace("_", " ").capitalize()

        messages = {
            "required": f"The {field_label} field is required.",
            "string": f"The {field_label} must be a string.",
            "integer": f"The {field_label} must be an integer.",
            "numeric": f"The {field_label} must be a number.",
            "boolean": f"The {field_label} must be a boolean.",
            "email": f"The {field_label} must be a valid email address.",
            "confirmed": f"The {field_label} confirmation does not match.",
        }

        if rule_name in messages:
            return messages[rule_name]

        if rule_name == "min":
            return f"The {field_label} must be at least {param}."
        if rule_name == "max":
            return f"The {field_label} may not be greater than {param}."
        if rule_name == "in":
            return f"The selected {field_label} is invalid."
        if rule_name == "not_in":
            return f"The selected {field_label} is invalid."
        if rule_name == "regex":
            return f"The {field_label} format is invalid."

        return f"Validation failed for field: {field_label}."
