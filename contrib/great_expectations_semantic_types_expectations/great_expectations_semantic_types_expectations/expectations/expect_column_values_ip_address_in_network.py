"""
This is a template for creating custom ColumnMapExpectations.
For detailed instructions on how to use it, please see:
    https://docs.greatexpectations.io/docs/guides/expectations/creating_custom_expectations/how_to_create_custom_column_map_expectations
"""

import ipaddress

from great_expectations.execution_engine import PandasExecutionEngine
from great_expectations.expectations.expectation import ColumnMapExpectation
from great_expectations.expectations.metrics import (
    ColumnMapMetricProvider,
    column_condition_partial,
)


def is_ip_address_in_network(addr: str, ip_network) -> bool:
    for ipn in ip_network:
        if ipaddress.ip_address(addr) in ipaddress.ip_network(ipn):
            return True
    return False


# This class defines a Metric to support your Expectation.
# For most ColumnMapExpectations, the main business logic for calculation will live in this class.
class ColumnValuesIpAddressInNetwork(ColumnMapMetricProvider):
    # This is the id string that will be used to reference your metric.
    condition_metric_name = "column_values.ip_address_in_network"
    condition_value_keys = ("ip_network",)

    # This method implements the core logic for the PandasExecutionEngine
    @column_condition_partial(engine=PandasExecutionEngine)
    def _pandas(cls, column, ip_network, **kwargs):
        return column.apply(lambda x: is_ip_address_in_network(x, ip_network))

    # This method defines the business logic for evaluating your metric when using a SqlAlchemyExecutionEngine
    # @column_condition_partial(engine=SqlAlchemyExecutionEngine)
    # def _sqlalchemy(cls, column, _dialect, **kwargs):
    #     raise NotImplementedError

    # This method defines the business logic for evaluating your metric when using a SparkDFExecutionEngine
    # @column_condition_partial(engine=SparkDFExecutionEngine)
    # def _spark(cls, column, **kwargs):
    #     raise NotImplementedError


# This class defines the Expectation itself
class ExpectColumnValuesIpAddressInNetwork(ColumnMapExpectation):
    """Expect column values to be IP addresses in the specified network ranges."""

    # These examples will be shown in the public gallery.
    # They will also be executed as unit tests for your Expectation.
    examples = [
        {
            "data": {
                "all_in": [
                    "192.168.0.0",
                    "192.168.0.1",
                    "192.168.0.2",
                    "192.168.0.3",
                    "192.168.0.254",
                ],
                "some_other": [
                    "213.181.199.16",
                    "213.181.199.16",
                    "213.181.199.16",
                    "213.181.199.16",
                    "142.250.180.206",
                ],
            },
            "tests": [
                {
                    "title": "basic_positive_test",
                    "exact_match_out": False,
                    "include_in_gallery": True,
                    "in": {
                        "column": "all_in",
                        "ip_network": ["192.168.0.0/24", "54.33.0.0/17"],
                    },
                    "out": {
                        "success": True,
                    },
                },
                {
                    "title": "basic_negative_test",
                    "exact_match_out": False,
                    "include_in_gallery": True,
                    "in": {
                        "column": "some_other",
                        "ip_network": ["192.168.0.0/24"],
                        "mostly": 0.9,
                    },
                    "out": {
                        "success": False,
                    },
                },
            ],
        }
    ]

    # This is the id string of the Metric used by this Expectation.
    # For most Expectations, it will be the same as the `condition_metric_name` defined in your Metric class above.
    map_metric = "column_values.ip_address_in_network"

    # This is a list of parameter names that can affect whether the Expectation evaluates to True or False
    success_keys = (
        "mostly",
        "ip_network",
    )

    # This dictionary contains default values for any parameters that should have default values
    default_kwarg_values = {}

    # This object contains metadata for display in the public Gallery
    library_metadata = {
        "maturity": "experimental",
        "tags": [
            "hackathon-22",
            "experimental",
            "typed-entities",
        ],  # Tags for this Expectation in the Gallery
        "contributors": [  # Github handles for all contributors to this Expectation.
            "@szecsip",  # Don't forget to add your github handle here!
        ],
    }

    success_keys = (
        "ip_network",
        "mostly",
    )


if __name__ == "__main__":
    ExpectColumnValuesIpAddressInNetwork().print_diagnostic_checklist()
