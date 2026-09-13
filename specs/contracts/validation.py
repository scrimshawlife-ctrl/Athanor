"""Advisory wire validation; performs no file access through manifest paths."""
import math
from jsonschema import Draft202012Validator, ValidationError


def validate_contract(instance, schema):
    """Schema formats plus semantics JSON Schema cannot express by itself."""
    required_formats = {'uri', 'date-time'}
    if not required_formats <= set(Draft202012Validator.FORMAT_CHECKER.checkers):
        raise RuntimeError('Missing URI/date-time format support: install specs/contracts/requirements.txt')
    Draft202012Validator(schema, format_checker=Draft202012Validator.FORMAT_CHECKER).validate(instance)
    # Python JSON readers may admit NaN/Infinity, which are not JSON numbers.
    def finite(value):
        if isinstance(value, float) and not math.isfinite(value):
            raise ValidationError('Non-finite JSON number')
        if isinstance(value, dict):
            for item in value.values():
                finite(item)
        elif isinstance(value, list):
            for item in value:
                finite(item)
    finite(instance)
    if instance.get('schema_version') != 'athanor.handoff.v1':
        return
    paths = set()
    reserved = {'con', 'prn', 'aux', 'nul'} | {f'{prefix}{n}' for prefix in ('com', 'lpt') for n in range(1, 10)}
    for artifact in instance['artifacts']:
        path = artifact['path'].casefold()
        if any(part.split('.')[0] in reserved for part in path.split('/')):
            raise ValidationError('Reserved device path')
        if path in paths:
            raise ValidationError('Duplicate normalized artifact path')
        paths.add(path)
    for path in paths:
        parts = path.split('/')
        if any('/'.join(parts[:i]) in paths for i in range(1, len(parts))):
            raise ValidationError('Artifact file/directory prefix collision')


def is_valid_contract(instance, schema):
    try:
        validate_contract(instance, schema)
        return True
    except ValidationError:
        return False

# Provenance: Notion Sprint 001 Hub [not inspected] + Loop 805 Slice N/A + Hash: 9013b524030b516de7baf6a42c3c1a32b829c958 (base)
