from typing import *
from pydantic import BaseModel, Field
from datetime import datetime
import enum

class PipelineConfig:
    def __init__(__pydantic_self__, _case_sensitive: 'bool | None' = None, _nested_model_default_partial_update: 'bool | None' = None, _env_prefix: 'str | None' = None, _env_prefix_target: 'EnvPrefixTarget | None' = None, _env_file: 'DotenvType | None' = WindowsPath('.'), _env_file_encoding: 'str | None' = None, _env_ignore_empty: 'bool | None' = None, _env_nested_delimiter: 'str | None' = None, _env_nested_max_split: 'int | None' = None, _env_parse_none_str: 'str | None' = None, _env_parse_enums: 'bool | None' = None, _cli_prog_name: 'str | None' = None, _cli_parse_args: 'bool | list[str] | tuple[str, ...] | None' = None, _cli_settings_source: 'CliSettingsSource[Any] | None' = None, _cli_parse_none_str: 'str | None' = None, _cli_hide_none_type: 'bool | None' = None, _cli_avoid_json: 'bool | None' = None, _cli_enforce_required: 'bool | None' = None, _cli_use_class_docs_for_groups: 'bool | None' = None, _cli_exit_on_error: 'bool | None' = None, _cli_prefix: 'str | None' = None, _cli_flag_prefix_char: 'str | None' = None, _cli_implicit_flags: "bool | Literal['dual', 'toggle'] | None" = None, _cli_ignore_unknown_args: 'bool | None' = None, _cli_kebab_case: "bool | Literal['all', 'no_enums'] | None" = None, _cli_shortcuts: 'Mapping[str, str | list[str]] | None' = None, _secrets_dir: 'PathType | None' = None, _build_sources: 'tuple[tuple[PydanticBaseSettingsSource, ...], dict[str, Any]] | None' = None, **values: 'Any') -> 'None':
        raise NotImplementedError()
    def construct(_fields_set: 'set[str] | None' = None, **values: 'Any') -> 'Self':
        raise NotImplementedError()
    def copy(self, *, include: 'AbstractSetIntStr | MappingIntStrAny | None' = None, exclude: 'AbstractSetIntStr | MappingIntStrAny | None' = None, update: 'Dict[str, Any] | None' = None, deep: 'bool' = False) -> 'Self':
        raise NotImplementedError()
    def dict(self, *, include: 'IncEx | None' = None, exclude: 'IncEx | None' = None, by_alias: 'bool' = False, exclude_unset: 'bool' = False, exclude_defaults: 'bool' = False, exclude_none: 'bool' = False) -> 'Dict[str, Any]':
        raise NotImplementedError()
    def from_orm(obj: 'Any') -> 'Self':
        raise NotImplementedError()
    def json(self, *, include: 'IncEx | None' = None, exclude: 'IncEx | None' = None, by_alias: 'bool' = False, exclude_unset: 'bool' = False, exclude_defaults: 'bool' = False, exclude_none: 'bool' = False, encoder: 'Callable[[Any], Any] | None' = PydanticUndefined, models_as_dict: 'bool' = PydanticUndefined, **dumps_kwargs: 'Any') -> 'str':
        raise NotImplementedError()
    def model_construct(_fields_set: 'set[str] | None' = None, **values: 'Any') -> 'Self':
        raise NotImplementedError()
    def model_copy(self, *, update: 'Mapping[str, Any] | None' = None, deep: 'bool' = False) -> 'Self':
        raise NotImplementedError()
    def model_dump(self, *, mode: "Literal['json', 'python'] | str" = 'python', include: 'IncEx | None' = None, exclude: 'IncEx | None' = None, context: 'Any | None' = None, by_alias: 'bool | None' = None, exclude_unset: 'bool' = False, exclude_defaults: 'bool' = False, exclude_none: 'bool' = False, exclude_computed_fields: 'bool' = False, round_trip: 'bool' = False, warnings: "bool | Literal['none', 'warn', 'error']" = True, fallback: 'Callable[[Any], Any] | None' = None, serialize_as_any: 'bool' = False, polymorphic_serialization: 'bool | None' = None) -> 'dict[str, Any]':
        raise NotImplementedError()
    def model_dump_json(self, *, indent: 'int | None' = None, ensure_ascii: 'bool' = False, include: 'IncEx | None' = None, exclude: 'IncEx | None' = None, context: 'Any | None' = None, by_alias: 'bool | None' = None, exclude_unset: 'bool' = False, exclude_defaults: 'bool' = False, exclude_none: 'bool' = False, exclude_computed_fields: 'bool' = False, round_trip: 'bool' = False, warnings: "bool | Literal['none', 'warn', 'error']" = True, fallback: 'Callable[[Any], Any] | None' = None, serialize_as_any: 'bool' = False, polymorphic_serialization: 'bool | None' = None) -> 'str':
        raise NotImplementedError()
    def model_json_schema(by_alias: 'bool' = True, ref_template: 'str' = '#/$defs/{model}', schema_generator: 'type[GenerateJsonSchema]' = <class 'pydantic.json_schema.GenerateJsonSchema'>, mode: 'JsonSchemaMode' = 'validation', *, union_format: "Literal['any_of', 'primitive_type_array']" = 'any_of') -> 'dict[str, Any]':
        raise NotImplementedError()
    def model_parametrized_name(params: 'tuple[type[Any], ...]') -> 'str':
        raise NotImplementedError()
    def model_post_init(self, context: 'Any', /) -> 'None':
        raise NotImplementedError()
    def model_rebuild(*, force: 'bool' = False, raise_errors: 'bool' = True, _parent_namespace_depth: 'int' = 2, _types_namespace: 'MappingNamespace | None' = None) -> 'bool | None':
        raise NotImplementedError()
    def model_validate(obj: 'Any', *, strict: 'bool | None' = None, extra: 'ExtraValues | None' = None, from_attributes: 'bool | None' = None, context: 'Any | None' = None, by_alias: 'bool | None' = None, by_name: 'bool | None' = None) -> 'Self':
        raise NotImplementedError()
    def model_validate_json(json_data: 'str | bytes | bytearray', *, strict: 'bool | None' = None, extra: 'ExtraValues | None' = None, context: 'Any | None' = None, by_alias: 'bool | None' = None, by_name: 'bool | None' = None) -> 'Self':
        raise NotImplementedError()
    def model_validate_strings(obj: 'Any', *, strict: 'bool | None' = None, extra: 'ExtraValues | None' = None, context: 'Any | None' = None, by_alias: 'bool | None' = None, by_name: 'bool | None' = None) -> 'Self':
        raise NotImplementedError()
    def parse_file(path: 'str | Path', *, content_type: 'str | None' = None, encoding: 'str' = 'utf8', proto: 'DeprecatedParseProtocol | None' = None, allow_pickle: 'bool' = False) -> 'Self':
        raise NotImplementedError()
    def parse_obj(obj: 'Any') -> 'Self':
        raise NotImplementedError()
    def parse_raw(b: 'str | bytes', *, content_type: 'str | None' = None, encoding: 'str' = 'utf8', proto: 'DeprecatedParseProtocol | None' = None, allow_pickle: 'bool' = False) -> 'Self':
        raise NotImplementedError()
    def schema(by_alias: 'bool' = True, ref_template: 'str' = '#/$defs/{model}') -> 'Dict[str, Any]':
        raise NotImplementedError()
    def schema_json(*, by_alias: 'bool' = True, ref_template: 'str' = '#/$defs/{model}', **dumps_kwargs: 'Any') -> 'str':
        raise NotImplementedError()
    def settings_customise_sources(settings_cls: 'type[BaseSettings]', init_settings: 'PydanticBaseSettingsSource', env_settings: 'PydanticBaseSettingsSource', dotenv_settings: 'PydanticBaseSettingsSource', file_secret_settings: 'PydanticBaseSettingsSource') -> 'tuple[PydanticBaseSettingsSource, ...]':
        raise NotImplementedError()
    def update_forward_refs(**localns: 'Any') -> 'None':
        raise NotImplementedError()
    def validate(value: 'Any') -> 'Self':
        raise NotImplementedError()
    pass
