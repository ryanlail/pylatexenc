from pylatexenc import latexwalker, latex2text, macrospec

#
# Define macros, environments, specials for the *parser*
#
lw_context_db = latexwalker.get_default_latex_context_db()
lw_context_db.add_context_category(
    'my-quotes',
    prepend=True,
    macros=[
        macrospec.MacroSpec("putindblquotes", "{"),
        macrospec.MacroSpec("putinquotes", "[[{"),
    ],
    environments=[
        macrospec.EnvironmentSpec("indblquotes", ""),
        macrospec.EnvironmentSpec("inquotes", "[["),
    ],
    specials=[
        macrospec.SpecialsSpec("`"),
        macrospec.SpecialsSpec("'"),
        macrospec.SpecialsSpec("``"),
        macrospec.SpecialsSpec("''"),
    ],
)

#
# Implement macros, environments, specials for the *conversion to text*
#

def _get_optional_arg(node, default, l2tobj):
    """Helper that returns the `node` converted to text, or `default`
    if the node is `None` (e.g. an optional argument that was not
    specified)"""
    if node is None:
        return default
    return l2tobj.nodelist_to_text([node])

def put_in_quotes_macro_repl(n, l2tobj):
    """Get the text replacement for the macro
    \putinquotes[open-quote][close-quote]{text}"""
    if not n.nodeargd:
        # n.nodeargd can be empty if e.g. \putinquotes was a single
        # token passed as an argument to a macro,
        # e.g. \newcommand\putinquotes...
        return ''
    open_q_s = _get_optional_arg(n.nodeargd.argnlist[0], '“', l2tobj)
    close_q_s = _get_optional_arg(n.nodeargd.argnlist[1], '”', l2tobj)
    return (open_q_s + l2tobj.nodelist_to_text([n.nodeargd.argnlist[2]])
            + close_q_s)

def in_quotes_env_repl(n, l2tobj):
    """Get the text replacement for the {inquotes} environment"""
    open_q_s = _get_optional_arg(n.nodeargd.argnlist[0], '“', l2tobj)
    close_q_s = _get_optional_arg(n.nodeargd.argnlist[1], '”', l2tobj)
    return open_q_s + l2tobj.nodelist_to_text(n.nodelist) + close_q_s

l2t_context_db = latex2text.get_default_latex_context_db()
l2t_context_db.add_context_category(
    'my-quotes',
    prepend=True,
    macros=[
        latex2text.MacroTextSpec("putindblquotes",
                                 simplify_repl=r'“%(1)s”'),
        latex2text.MacroTextSpec("putinquotes",
                                 simplify_repl=put_in_quotes_macro_repl),
    ],
    environments=[
        latex2text.EnvironmentTextSpec("indblquotes",
                                       simplify_repl=r'“%(body)s”'),
        latex2text.EnvironmentTextSpec("inquotes",
                                       simplify_repl=in_quotes_env_repl),
    ],
    specials=[
        latex2text.SpecialsTextSpec('`', "‘"),
        latex2text.SpecialsTextSpec("'", "’"),
        latex2text.SpecialsTextSpec('``', "“"),
        latex2text.SpecialsTextSpec("''", "”"),
    ],
)


#
# Here is an example usage:
#

def custom_latex_to_text( input_latex ):
    # the latex parser instance with custom latex_context
    lw_obj = latexwalker.LatexWalker(input_latex,
                                     latex_context=lw_context_db)
    # parse to node list
    nodelist, pos, length = lw_obj.get_latex_nodes()
    # initialize the converter to text with custom latex_context
    l2t_obj = latex2text.LatexNodes2Text(latex_context=l2t_context_db)
    # convert to text
    return l2t_obj.nodelist_to_text( nodelist )


print(custom_latex_to_text(
    r"""\begin{inquotes}[`][']Hello, world\end{inquotes}"""))
# ‘Hello, world’

print(custom_latex_to_text(r"""\putinquotes[``]['']{Hello, world}"""))
# “Hello, world”

print(custom_latex_to_text(r"""\putinquotes{Hello, world}"""))
# “Hello, world”

print(custom_latex_to_text(r"""\putinquotes[`][']{Hello, world}"""))
# ‘Hello, world’
