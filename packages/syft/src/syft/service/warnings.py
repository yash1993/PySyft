# stdlib
from typing import Optional

# third party
from IPython.display import display
from rich.prompt import Confirm

# relative
from ..abstract_node import AbstractNode
from ..abstract_node import NodeSideType
from ..node.credentials import SyftCredentials
from ..serde.serializable import serializable
from ..types.syft_object import Context
from ..util.experimental_flags import flags
from .response import SyftResponseMessage
from .user.user_roles import ServiceRole


class WarningContext(
    Context,
):
    node: Optional[AbstractNode]
    credentials: Optional[SyftCredentials]
    role: ServiceRole


@serializable()
class APIEndpointWarning(SyftResponseMessage):
    confirmation: bool = False
    message: Optional[str] = None

    @property
    def _repr_html_class_(self) -> str:
        return "alert-warning"

    def __repr__(self) -> str:
        return f"SyftWarning: {self.message}"

    def message_from(self, context: Optional[WarningContext]):
        raise NotImplementedError

    def show(self):
        if not self.message:
            return True
        display(self)
        if self.confirmation and flags.PROMPT_ENABLED:
            allowed = Confirm.ask("Would you like to proceed?")
            if not allowed:
                display("Aborted !!")
                return False
        return True


@serializable()
class CRUDWarning(APIEndpointWarning):
    def message_from(self, context: Optional[WarningContext] = None):
        message = None
        if context is not None:
            node = context.node
            node_side_type = node.node_side_type
            node_type = node.node_type
            _msg = (
                "which could host datasets with private information."
                if node_side_type.value == NodeSideType.HIGH_SIDE.value
                else "which only hosts mock or synthetic data."
            )
            message = (
                "You're performing an operation on "
                f"{node_side_type.value} side {node_type.value}, {_msg}"
            )
            self.confirmation = node_side_type.value == NodeSideType.HIGH_SIDE.value
            self.message = message


@serializable()
class CRUDReminder(CRUDWarning):
    confirmation: bool = False

    def message_from(self, context: Optional[WarningContext] = None):
        message = None
        if context is not None:
            node = context.node
            node_side_type = node.node_side_type
            node_type = node.node_type
            _msg = (
                "which could host datasets with private information."
                if node_side_type.value == NodeSideType.HIGH_SIDE.value
                else "which only hosts mock or synthetic data."
            )
            message = (
                "You're performing an operation on "
                f"{node_side_type.value} side {node_type.value}, {_msg}"
            )
            self.message = message


@serializable()
class LowSideCRUDWarning(APIEndpointWarning):
    def message_from(self, context: Optional[WarningContext] = None):
        if context is not None:
            node = context.node
            node_side_type = node.node_side_type
            node_type = node.node_type
            if node_side_type.value == NodeSideType.LOW_SIDE.value:
                message = (
                    "You're performing an operation on "
                    f"{node_side_type.value} side {node_type.value} "
                    "which only hosts mock or synthetic data."
                )

            self.message = message


@serializable()
class HighSideCRUDWarning(APIEndpointWarning):
    def message_from(self, context: Optional[WarningContext] = None):
        if context is not None:
            node = context.node
            node_side_type = node.node_side_type
            node_type = node.node_type
            if node_side_type.value == NodeSideType.HIGH_SIDE.value:
                message = (
                    "You're performing an operation on "
                    f"{node_side_type.value} side {node_type.value} "
                    "which could host datasets with private information."
                )
                self.message = message
