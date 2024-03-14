from __future__ import annotations

from enum import Enum
from functools import cached_property
from typing import TYPE_CHECKING, Any, Optional

from great_expectations.core.expectation_validation_result import (
    ExpectationSuiteValidationResult,
    ExpectationValidationResult,
)
from great_expectations.validator.validator import Validator as OldValidator
from great_expectations.validator.validator import calc_validation_statistics

if TYPE_CHECKING:
    from great_expectations.core import ExpectationSuite
    from great_expectations.core.batch_config import BatchConfig
    from great_expectations.datasource.fluent.batch_request import BatchRequestOptions
    from great_expectations.expectations.expectation import (
        Expectation,
        ExpectationConfiguration,
    )


class ResultFormat(str, Enum):
    BOOLEAN_ONLY = "BOOLEAN_ONLY"
    BASIC = "BASIC"
    SUMMARY = "SUMMARY"
    COMPLETE = "COMPLETE"


class Validator:
    """Validator.

    Responsible for running expectations on a batch configuration.
    """

    def __init__(
        self,
        batch_config: BatchConfig,
        result_format: ResultFormat = ResultFormat.SUMMARY,
        batch_request_options: Optional[BatchRequestOptions] = None,
    ) -> None:
        self._batch_config = batch_config
        self._batch_request_options = batch_request_options
        self.result_format = result_format

        from great_expectations import project_manager

        self._get_validator = project_manager.get_validator

    def validate_expectation(
        self,
        expectation: Expectation,
        evaluation_parameters: Optional[dict[str, Any]] = None,
    ) -> ExpectationValidationResult:
        """Run a single expectation against the batch config"""
        results = self._validate_expectation_configs([expectation.configuration])

        assert len(results) == 1
        return results[0]

    def validate_expectation_suite(
        self,
        expectation_suite: ExpectationSuite,
        evaluation_parameters: Optional[dict[str, Any]] = None,
    ) -> ExpectationSuiteValidationResult:
        """Run an expectation suite against the batch config"""
        results = self._validate_expectation_configs(
            expectation_suite.expectation_configurations,
            evaluation_parameters,
        )
        statistics = calc_validation_statistics(results)

        # TODO: This was copy/pasted from Validator, but many fields were removed
        return ExpectationSuiteValidationResult(
            results=results,
            success=statistics.success,
            statistics={
                "evaluated_expectations": statistics.evaluated_expectations,
                "successful_expectations": statistics.successful_expectations,
                "unsuccessful_expectations": statistics.unsuccessful_expectations,
                "success_percent": statistics.success_percent,
            },
        )

    @property
    def active_batch_id(self) -> Optional[str]:
        return self._wrapped_validator.active_batch_id

    @cached_property
    def _wrapped_validator(self) -> OldValidator:
        batch_request = self._batch_config.build_batch_request(
            batch_request_options=self._batch_request_options
        )
        return self._get_validator(batch_request=batch_request)

    def _validate_expectation_configs(
        self,
        expectation_configs: list[ExpectationConfiguration],
        evaluation_parameters: Optional[dict[str, Any]] = None,
    ) -> list[ExpectationValidationResult]:
        """Run a list of expectation configurations against the batch config"""
        processed_expectation_configs = (
            self._wrapped_validator.process_expectations_for_validation(
                expectation_configs, evaluation_parameters
            )
        )

        results = self._wrapped_validator.graph_validate(
            configurations=processed_expectation_configs,
            runtime_configuration={"result_format": self.result_format.value},
        )

        return results
