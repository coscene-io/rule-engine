# Copyright 2024 coScene
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from dataclasses import dataclass
from inspect import Parameter, signature

from ruleengine.dsl.base_actions import create_moment_factory, upload_factory


@dataclass
class UnknownFunctionKeywordArgException(Exception):
    name: str


class ActionValidator:
    def __init__(self, action_impls):
        self.__impls = action_impls

    def upload(self, *args, **kwargs):
        def validate_arg_types(args):
            def check_is_list_of_string(name):
                value = args.get(name, [])
                if not isinstance(value, list) or any(
                    not isinstance(i, str) for i in value
                ):
                    # TODO: Make this an actual error instead of a generic error
                    raise Exception(f"{name} must be list of strings")

            check_is_list_of_string("labels")
            check_is_list_of_string("extra_files")
            check_is_list_of_string("white_list")

            if not isinstance(args.get("before", 0), int):
                # TODO: Make this an actual error instead of a generic error
                raise Exception("before must be an int")

            if not isinstance(args.get("after", 0), int):
                # TODO: Make this an actual error instead of a generic error
                raise Exception("after must be an int")

        return self._validate_factory_func(
            upload_factory(self.__impls["upload"]),
            args,
            kwargs,
            validate_arg_types,
        )

    def create_moment(self, *args, **kwargs):
        def validate_arg_types(args):
            assign_to = args.get("assign_to", "")
            if not isinstance(assign_to, str):
                # TODO: Make this an actual error instead of a generic error
                raise Exception("assign_to must be string")

        return self._validate_factory_func(
            create_moment_factory(self.__impls["create_moment"]),
            args,
            kwargs,
            validate_arg_types,
        )

    def _validate_factory_func(self, factory, args, kwargs, param_type_check):
        sig = signature(factory)

        # We first do a manual check of the args to ensure the correct number
        # of parameters, and the right keyword args are passed. We don't use the
        # `bind` call below because it raises a TypeError, and we can't extract
        # the failure reason to report back to the user
        self._validate_signature(sig, args, kwargs)

        param_type_check(sig.bind(*args, **kwargs).arguments)

        return factory(*args, **kwargs)

    def _validate_signature(self, sig, args, kwargs):
        if len(args) > len(sig.parameters):
            raise Exception("too many arguments")

        for key in kwargs:
            if key not in sig.parameters:
                raise UnknownFunctionKeywordArgException(key)

        for i, (name, param) in enumerate(sig.parameters.items()):
            if i < len(args):
                if name in kwargs:
                    raise Exception(f"multiple values given for `{name}`")
            else:
                if name not in kwargs and param.default is Parameter.empty:
                    raise Exception(f"value not specified for parameter `{name}`")
