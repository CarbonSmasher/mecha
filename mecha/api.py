__all__ = [
    "Mecha",
    "MechaOptions",
]


from contextlib import contextmanager
from dataclasses import InitVar, dataclass
from typing import Any, Iterator, Optional, Type, TypeVar, Union, overload

from beet import Context, TextFileBase
from beet.core.file import TextFile
from beet.core.utils import extra_field
from pydantic import BaseModel
from tokenstream import TokenStream

from .ast import AstNode, AstRoot
from .parse import delegate, get_default_parsers
from .serialize import Serializer
from .spec import CommandSpec

AstNodeType = TypeVar("AstNodeType", bound=AstNode)


class MechaOptions(BaseModel):
    """Mecha options."""

    multiline: bool = False


@dataclass
class Mecha:
    """Class exposing the command api."""

    ctx: InitVar[Optional[Context]] = None
    multiline: InitVar[bool] = False

    spec: CommandSpec = extra_field(
        default_factory=lambda: CommandSpec(parsers=get_default_parsers())
    )

    serialize: Serializer = extra_field(init=False)

    def __post_init__(self, ctx: Optional[Context], multiline: bool):
        if ctx:
            opts = ctx.validate("mecha", MechaOptions)
            self.spec.multiline = opts.multiline
        else:
            self.spec.multiline = multiline

        self.serialize = Serializer(self.spec)

    @contextmanager
    def prepare_token_stream(
        self,
        stream: TokenStream,
        multiline: Optional[bool] = None,
    ) -> Iterator[TokenStream]:
        """Prepare the token stream for parsing."""
        with stream.reset(*stream.data), stream.provide(
            spec=self.spec,
            multiline=self.spec.multiline if multiline is None else multiline,
        ):
            with stream.reset_syntax(comment=r"#.+$", literal=r"\S+"):
                with stream.indent(skip=["comment"]), stream.ignore("indent", "dedent"):
                    with stream.intercept("newline", "eof"):
                        yield stream

    @overload
    def parse(
        self,
        source: Union[TextFileBase[Any], str],
        *,
        filename: Optional[str] = None,
        resource_location: Optional[str] = None,
        multiline: Optional[bool] = None,
    ) -> AstRoot:
        ...

    @overload
    def parse(
        self,
        source: Union[TextFileBase[Any], str],
        *,
        type: Type[AstNodeType],
        filename: Optional[str] = None,
        resource_location: Optional[str] = None,
        multiline: Optional[bool] = None,
    ) -> AstNodeType:
        ...

    def parse(
        self,
        source: Union[TextFileBase[Any], str],
        *,
        type: Optional[Type[AstNode]] = None,
        filename: Optional[str] = None,
        resource_location: Optional[str] = None,
        multiline: Optional[bool] = None,
    ) -> Any:
        """Parse the given source into an AST."""
        if not type:
            type = AstRoot

        if not type.parser:
            raise TypeError(f"No parser directly associated with {type}.")

        if isinstance(source, str):
            source = TextFile(source)

        if not filename and source.source_path:
            filename = str(source.source_path)

        # TODO: Wrap errors in a clean FormattedPipelineException

        stream = TokenStream(source.text)
        with self.prepare_token_stream(stream, multiline=multiline):
            return delegate(type.parser, stream)
